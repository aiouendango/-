from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

# 環境変数から取得（Renderの環境設定で登録しておくこと）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    event = body["events"][0]
    reply_token = event["replyToken"]
    user_message = event["message"]["text"]

    # ChatGPTに問い合わせ
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは親切な応援団のAIです。"},
            {"role": "user", "content": user_message}
        ]
    )
    reply_message = response["choices"][0]["message"]["content"]

    # LINEに返答
    reply_to_line(reply_token, reply_message)

    return "OK", 200

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
    requests.post("https://api.line.me/v2/bot/message/reply", json=payload, headers=headers)
