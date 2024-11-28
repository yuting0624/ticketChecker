# Disney Ticket Checker

ある旅行サイトにおいて、自動的にディズニーランド/ディズニーシーのチケット空き状況をチェックし、チケットが見つかった場合にDiscord通知を送信するPythonスクリプトです。

## 機能

- 東京ディズニーランドと東京ディズニーシーのチケット空き状況を自動チェック
- チケットが見つかった場合、Discord経由でリアルタイム通知
- スクリーンショットの自動保存（チケット発見時およびエラー発生時）
- 詳細なログ記録
- 10分間隔での自動チェック
- エラー発生時の自動リトライ機能

## 必要要件

- Python 3.x
- Google Chrome
- Discordアカウントおよびサーバー権限（通知用）

## インストール

1. リポジトリのクローン:
```bash
git clone https://github.com/your-username/disney-ticket-checker.git
cd disney-ticket-checker
```

2. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

## 設定

1. Discord Webhookの設定:
   - Discordサーバーを開く
   - 通知を送信したいチャンネルの設定を開く（歯車アイコン）
   - 「インテグレーション」→「Webhook作成」をクリック
   - Webhook URLをコピー

2. プログラムの設定:
   - `main.py`の以下の設定値を更新:
```python
PASSWORD = "パスワード"
DISCORD_WEBHOOK_URL = "あなたのDiscord Webhook URL"
```

## 使用方法

### 通知テスト

1. `main.py`内の`TEST_MODE`を`True`に設定:
```python
TEST_MODE = True
```

2. プログラムを実行:
```bash
python main.py
```



### 通常モード

1. `main.py`内の`TEST_MODE`を`False`に設定:
```python
TEST_MODE = False
```

2. プログラムを実行:
```bash
python main.py
```

プログラムは10分ごとにチケットの空き状況をチェックし、チケットが見つかった場合はDiscordで通知します。

## ログとスクリーンショット

- ログファイル: `ticket_checker.log`
- チケット発見時のスクリーンショット: `ticket_found_[park]_[timestamp].png`
- エラー時のスクリーンショット: `error_[park]_[timestamp].png`

## エラーハンドリング

- ネットワークエラーやブラウザエラーが発生した場合、自動的にリトライします
- エラーが発生した場合、詳細なログとスクリーンショットが保存されます

## トラブルシューティング

1. ChromeDriverのエラー:
   - Google Chromeを最新版にアップデート
   - `webdriver_manager`が自動的に適切なドライバーをインストール

2. Discord通知が届かない:
   - Webhook URLが正しく設定されているか確認
   - インターネット接続を確認
   - Discordサーバーの権限設定を確認

3. チケットチェックが失敗する:
   - ログファイルでエラーメッセージを確認
   - スクリーンショットで問題の状況を確認
   - パスワードが正しく設定されているか確認

## 注意事項

- このスクリプトは個人利用を目的としています
- 過度なアクセスを避けるため、チェック間隔は適切に設定してください
- パスワードなどの機密情報の取り扱いには十分注意してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能改善の提案は、GitHubのIssuesで受け付けています。

---
