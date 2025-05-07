from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

# 環境変数から取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.json
        print("受信データ:", body)  # ★ デバッグ用

        event = body["events"][0]
        if event["type"] != "message" or "text" not in event["message"]:
            return "Not a text message", 200

        reply_token = event["replyToken"]
        user_message = event["message"]["text"]

        # ChatGPTへ問い合わせ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切な応援団のAIです。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply_message = response["choices"][0]["message"]["content"]

        # LINEへ返答
        reply_to_line(reply_token, reply_message)
        return "OK", 200

    except Exception as e:
        print("エラー:", str(e))
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
