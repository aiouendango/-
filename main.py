from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

# 環境変数から取得（Renderで設定済みであること）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.get_json()
        print("Received request body:", body)

        if "events" not in body or len(body["events"]) == 0:
            return "No event", 200

        event = body["events"][0]
        if event.get("type") != "message" or event["message"].get("type") != "text":
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
