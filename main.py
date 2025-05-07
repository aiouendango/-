from flask import Flask, request
import os
import requests
import openai
import json
import traceback

app = Flask(__name__)

# 環境変数からキーを取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAIのAPIキーを設定
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.get_json()
        print("✅ 受信データ:", json.dumps(body, indent=2, ensure_ascii=False))

        if "events" not in body or len(body["events"]) == 0:
            print("⚠️ イベントなし")
            return "No event", 200

        event = body["events"][0]
        if event.get("type") != "message" or event["message"].get("type") != "text":
            print("⚠️ テキストメッセージではない")
            return "Not a text message", 200

        reply_token = event["replyToken"]
        user_message = event["message"]["text"]

        # ChatGPTへのリクエスト
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは優しい応援団のAIです"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_message = response["choices"][0]["message"]["content"]

        # LINEへの返信
        reply_to_line(reply_token, reply_message)
        return "OK", 200

    except Exception as e:
        print("❌ エラー:", str(e))
        print(traceback.format_exc())
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
    print("📨 LINE応答:", response.status_code, response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
