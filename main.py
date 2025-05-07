from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI応援団 Bot 動いてます！", 200
