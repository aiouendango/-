from flask import Flask, request
import os
import requests
import openai

app = Flask(__name__)

# 環境変数からAPIキーを取得
openai_api_key = os.environ.get("OPENAI_API_KEY")
line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

client = openai.OpenAI(api_key=openai_api_key)

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
        print("イベント内容:", event)

        if event.get("type") != "message" or event["message"].get("type") != "text":
            return "Not a text message", 200

        reply_token = event["replyToken"]
        user_message = event["message"]["text"]

        # ChatGPTに問い合わせ（OpenAI Python SDK v1対応）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは優しい応援団のAIです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_message = response.choices[0].message.content
        print("AI返信:", reply_message)

        reply_to_line(reply_token, reply_message)
        return "OK", 200

    except Exception as e:
        print("エラー:", str(e))
        return "Internal Server Error", 500

def reply_to_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_token}"
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
    print("LINE応答ステータス:", response.status_code)
    print("LINE応答本文:", response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)