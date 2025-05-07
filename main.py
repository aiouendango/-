from flask import Flask, request
from openai import OpenAI
import requests
import os
import traceback

app = Flask(__name__)

# 環境変数から取得（Renderの「Environment Variables」に設定しておくこと）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAIのクライアント初期化
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.get_json()
        print("受信データ:", body)

        if "events" not in body or len(body["events"]) == 0:
            return "No event", 200

        event = body["events"][0]
        if event.get("type") != "message" or event["message"].get("type") != "text":
            return "Not a text message", 200

        reply_token = event["replyToken"]
        user_message = event["message"]["text"]

        # ChatGPTへ問い合わせ（OpenAI SDK v1対応）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な応援団のAIです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_message = response.choices[0].message.content

        # LINEに返答
        reply_to_line(reply_token, reply_message)
        return "OK", 200

    except Exception as e:
        print("エラー:", str(e))
        traceback.print_exc()  # ← 詳細エラーを表示
        return "Internal Server Error", 500

def reply_to_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=payload
    )
    print("LINE応答:", response.status_code, response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
