import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from database import User, db

load_dotenv(override=True)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

@app.route("/callback", methods=["POST"])
def callback():
    """Messaging APIからの呼び出し関数"""
    # LINEがリクエストの改ざんを防ぐために付与する署名を取得
    signature = request.headers["X-Line-Signature"]
    # リクエストの内容をテキストで取得
    body = request.get_data(as_text=True)
    # ログに出力
    app.logger.info("Request body: " + body)

    try:
        # signature と body を比較することで、リクエストがLINEから送信されたものであることを検証
        handler.handle(body, signature)
    except InvalidSignatureError:
        # クライアントからのリクエストに誤りがあったことを示すエラーを返す
        abort(400)

    return "OK"


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
        
        # 管理者向けにプッシュメッセージを送信
        message_to_admin = TextSendMessage(text=f"{user_name}さんが回覧板の確認を完了しました。")
        line_bot_api.push_message(ADMIN_USER_ID, messages=message_to_admin)

        # ユーザーに確認完了メッセージを返信
        reply_message_to_user = TextSendMessage(text="回覧板の確認を受け付けました！ありがとうございます！")
        line_bot_api.reply_message(event.reply_token, messages=reply_message_to_user)

# ローカルでの動作テスト用
if __name__ == "__main__":
    app.run(debug=True)
