# 必要なライブラリをインポート
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os  # osモジュールをインポート

# Flaskアプリを初期化
app = Flask(__name__)

# ★★★ ここにLINE Developersで取得した情報を設定する ★★★
YOUR_CHANNEL_ACCESS_TOKEN = "あなたのチャンネルアクセストークン"
YOUR_CHANNEL_SECRET = "あなたのチャンネルシークレット"

# .envファイルなどから管理者IDを取得する
# 環境変数が設定されていない場合に備え、Noneを許容する
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")

# LINEボットのAPIとWebhookハンドラーを初期化
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


# LINEからのメッセージを受け取るためのエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    # LINEからのリクエストヘッダーにある署名を取得
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        # 署名を検証し、問題がなければハンドラーにイベントを渡す
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名が不正な場合はエラーを返す
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# メッセージイベントが発生したときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザーが送ったメッセージを取得
    message_text = event.message.text
    user_id = event.source.user_id

    # 特定のキーワードかどうかをチェック
    if message_text.startswith("check_done_"):
        # プロフィール情報を取得
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        
        # 管理者IDが設定されている場合のみ、プッシュメッセージを送信
        if ADMIN_USER_ID:
            message_to_admin = TextSendMessage(text=f"{user_name}さんが回覧板の確認を完了しました。")
            line_bot_api.push_message(ADMIN_USER_ID, messages=message_to_admin)
        else:
            # 管理者IDが設定されていない場合のログ出力（任意）
            app.logger.warning("ADMIN_USER_ID is not set. Push message to admin skipped.")

        # ユーザーに確認完了メッセージを返信
        reply_message_to_user = TextSendMessage(text="回覧板の確認を受け付けました！ありがとうございます！")
        line_bot_api.reply_message(event.reply_token, messages=reply_message_to_user)

# ローカルでの動作テスト用
if __name__ == "__main__":
    app.run(debug=True)
