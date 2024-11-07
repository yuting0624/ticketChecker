from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import json

# ロギングの設定を詳細にする
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ticket_checker.log'),
        logging.StreamHandler()  # コンソールにも出力
    ]
)

class TicketChecker:
    def __init__(self, password, discord_webhook_url):
        self.url = "https://reserva.be/kansyasai2024/aikotoba"
        self.password = password
        self.discord_webhook_url = discord_webhook_url
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Webドライバーの初期設定"""
        try:
            options = webdriver.ChromeOptions()
            
            # 安定性のための追加オプション
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--silent')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--window-size=1920,1080')
            
            # User-Agentの設定
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            # ヘッドレスモードの設定（必要に応じてコメントアウト）
            # options.add_argument('--headless=new')
            
            # ChromeDriverManagerを使用して最新のドライバーを自動設定
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            logging.info("ブラウザ設定完了")
            return True
            
        except Exception as e:
            logging.error(f"ブラウザ設定中にエラー: {str(e)}")
            return False
        
    def wait_and_find_element(self, by, value, timeout=20):
        """要素が見つかるまで待機して取得"""
        try:
            logging.info(f"要素を探索中: {by} = {value}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logging.info("要素を発見")
            return element
        except TimeoutException:
            logging.error(f"要素が見つかりませんでした: {value}")
            # 現在のページのHTMLをログに記録
            logging.error(f"現在のページのURL: {self.driver.current_url}")
            logging.error(f"現在のページのタイトル: {self.driver.title}")
            raise
        
    def login(self):
        """サイトにログイン"""
        try:
            logging.info(f"サイトにアクセス開始: {self.url}")
            self.driver.get(self.url)
            logging.info("サイトにアクセス成功")
            
            # ページロード完了を確認
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # パスワード入力欄が表示されるまで待機
            logging.info("パスワード入力欄を探索中")
            password_input = self.wait_and_find_element(
                By.CSS_SELECTOR, 
                "input.textbox.textbox--long.password__form[name='bus_aikotoba_answer']"
            )
            password_input.clear()
            password_input.send_keys(self.password)
            logging.info("パスワード入力完了")
            
            # ログインボタンをクリック
            logging.info("ログインボタンを探索中")
            login_button = self.wait_and_find_element(
                By.CSS_SELECTOR,
                "button.btn.btn--main"
            )
            login_button.click()
            logging.info("ログインボタンクリック完了")
            
            # ログイン後のページ読み込みを待機
            time.sleep(3)
            
            # ログイン成功の確認（例：特定の要素の存在確認）
            try:
                self.wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("ログイン後のページ読み込み完了")
                return True
            except:
                logging.error("ログイン後のページ読み込みに失敗")
                return False
            
        except Exception as e:
            logging.error(f"ログイン処理中にエラー: {str(e)}")
            return False
        
    def send_discord_notification(self, park):
        """Discord通知の送信"""
        try:
            park_name = "東京ディズニーランド" if park == "land" else "東京ディズニーシー"
            
            # Discordメッセージの作成
            message = {
                "embeds": [{
                    "title": f"🎫 チケット空き通知 - {park_name}",
                    "description": f"""
                        **チケットに空きが見つかりました！**
                        
                        🎢 パーク: {park_name}
                        🕒 確認時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        🌐 予約サイト:
                        {self.url}
                        
                        ⚡ 至急ご確認ください！
                    """,
                    "color": 5814783,  # 水色
                    "footer": {
                        "text": "Disney Ticket Checker"
                    }
                }]
            }
            
            # Discord Webhookに送信
            response = requests.post(
                self.discord_webhook_url,
                json=message
            )
            
            if response.status_code == 204:
                logging.info(f"Discord通知送信成功: {park_name}")
            else:
                logging.error(f"Discord通知送信失敗: ステータスコード {response.status_code}")
                
        except Exception as e:
            logging.error(f"Discord通知送信失敗: {str(e)}")

    
    def check_tickets(self, park):
        """チケットの空き状況をチェック"""
        try:
            # パークタイトルとボタンの要素を特定
            if park == "land":
                title_text = "Tokyo Disneyland Park Ticket"
            else:
                title_text = "Tokyo DisneySea Park Ticket"
            
            logging.info(f"{park}のチケット情報を確認中")
            
            # タイトル要素を探す
            park_element = self.wait_and_find_element(
                By.XPATH,
                f"//div[contains(@class, 'menu__outline__title') and contains(text(), '{title_text}')]"
            )
            
            # 予約ボタンを探す（同じmenu__outline内）
            book_button = park_element.find_element(
                By.XPATH,
                "..//span[contains(@class, 'btn--main') and contains(text(), 'Book')]"
            )
            
            # ボタンが見えるようにスクロール
            self.driver.execute_script("arguments[0].scrollIntoView(true);", book_button)
            time.sleep(1)
            
            # ボタンをクリック
            book_button.click()
            logging.info(f"{park}の予約ボタンをクリック")
            
            # ページ遷移を待機
            time.sleep(3)
            
            # 人数選択の+ボタンを2回クリック
            plus_button = self.wait_and_find_element(
                By.CSS_SELECTOR,
                "span.num-trigger.js-customers-increase[data-target='charge_type_0']"
            )
            for _ in range(2):
                plus_button.click()
                time.sleep(0.5)
            
            logging.info("人数を2名に設定")
            
            # 次へボタンをクリック
            next_button = self.wait_and_find_element(
                By.CSS_SELECTOR,
                "a.btn.btn--sub.js-userselect-next[data-target='userselect-datetime']"
            )
            next_button.click()
            logging.info("次へボタンをクリック")
            
            # 少し待機してメッセージを確認
            time.sleep(2)
            
            try:
                # チケットなしメッセージを確認
                no_tickets_message = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "p.alert.is-active#err-userselect-customers"
                )
                if "No available schedule" in no_tickets_message.text:
                    logging.info(f"{park}: チケットなし")
                    
                    # 前のページに戻る
                    self.driver.back()
                    time.sleep(2)
                    
                    return False
                    
            except NoSuchElementException:
                # カレンダーが表示されているか確認（チケットあり）
                try:
                    calendar = self.wait_and_find_element(
                        By.CSS_SELECTOR,
                        ".calendar-select",  # カレンダーのセレクターは実際のものに合わせて調整が必要
                        timeout=5
                    )
                    logging.info(f"{park}: チケット発見！カレンダーが表示されています")
                    
                    # スクリーンショットを保存
                    screenshot_path = f"ticket_found_{park}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logging.info(f"スクリーンショット保存: {screenshot_path}")

                    # Discord通知を送信
                    self.send_discord_notification(park)
                    
                    # 前のページに戻る
                    self.driver.back()
                    time.sleep(2)
                    
                    return True
                    
                except TimeoutException:
                    logging.error(f"{park}: カレンダーが見つかりません")
                    
                    # 前のページに戻る
                    self.driver.back()
                    time.sleep(2)
                    
                    return False
                
        except Exception as e:
            logging.error(f"チケットチェック中にエラー ({park}): {str(e)}")
            # エラー発生時のスクリーンショットを保存
            error_screenshot = f"error_{park}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(error_screenshot)
            logging.error(f"エラー時のスクリーンショット: {error_screenshot}")
            return False

    def send_notification(self, park):
        """メール通知の送信"""
        try:
            park_name = "東京ディズニーランド" if park == "land" else "東京ディズニーシー"
            subject = f"ディズニーチケット空き通知 - {park_name}"
            body = f"""
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            {park_name}のチケットに空きが見つかりました！
            
            予約サイトURL:
            {self.url}
            
            至急ご確認ください。
            """
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email_sender
            msg['To'] = self.email_receiver
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.email_sender, self.email_password)
                smtp.send_message(msg)
                
            logging.info(f"通知メール送信成功: {park_name}")
            
        except Exception as e:
            logging.error(f"メール送信失敗: {str(e)}")
    
    def run_check(self):
        """メインの実行関数"""
        try:
            if not self.setup_driver():
                logging.error("ブラウザの設定に失敗しました")
                return
                
            if not self.login():
                logging.error("ログインに失敗しました")
                return
                
            parks = ["land", "sea"]
            for park in parks:
                try:
                    if self.check_tickets(park):
                        self.send_notification(park)
                    time.sleep(2)
                except Exception as e:
                    logging.error(f"{park}のチェック中にエラー: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"実行中にエラー: {str(e)}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("ブラウザを正常に終了")
                except:
                    logging.error("ブラウザの終了に失敗")

    def test_notification(self):
        """通知機能のテスト用メソッド"""
        try:
            logging.info("Discord通知機能のテストを開始")
            self.send_discord_notification("land")
            time.sleep(2)
            self.send_discord_notification("sea")
            logging.info("Discord通知機能のテスト完了")
        except Exception as e:
            logging.error(f"通知テスト中にエラー: {str(e)}")


def main():
    # 設定値
    PASSWORD = "ibm2024"
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1303923894792617984/kmXGoJBWhY4NwkV9yFprV8fXsBmyMKIpc_k9WSi9zKs7wkWyO588QiiHF22AYa-yJWrw"
    
    checker = TicketChecker(PASSWORD, DISCORD_WEBHOOK_URL)
    
    # テストモードフラグ
    TEST_MODE = False  # テストを実行する場合はTrueに設定
    
    if TEST_MODE:
        # テスト実行
        checker.test_notification()
    else:
        # 通常の実行
        while True:
            try:
                checker.run_check()
                logging.info("チェック完了、10分待機します")
                time.sleep(600)
            except Exception as e:
                logging.error(f"メインループでエラー: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    main()