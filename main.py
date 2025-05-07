from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "AI‰‰‡’c Bot “®‚¢‚Ä‚Ü‚·I", 200
