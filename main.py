from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

# 環境変数からキーを取得（Renderで設定済みであること）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAIクライアント（v1系対応）
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.get_json()
        print("Received:", body)

        if "events" not in body or not body["events"]:
            return "No events", 200

        event = body["events"][0]
        if event.get("type") != "message" or event["message"].get("type") != "text":
            return "Unsupported event type", 200

        user_message = event["message"]["text"]
        reply_token = event["replyToken"]

        # OpenAIへ問い合わせ
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な応援団のAIです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_message = chat_response.choices[0].message.content

        # LINEに返信
        reply_to_line(reply_token, reply_message)
        return "OK", 200

    except Exception as e:
        print("エラー:", e)
        return "Internal Server Error", 500

def reply_to_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=payload
    )
    print("LINE返信:", response.status_code, response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
