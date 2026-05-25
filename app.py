import os
import json
import hashlib
import hmac
import base64
import requests as req
from flask import Flask, request, abort

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from bot import GrowthBot

app = Flask(__name__)
bot = GrowthBot()

def verify_signature(body, signature):
    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    return hmac.compare_digest(expected_signature, signature)

def reply_message(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }
    req.post(url, headers=headers, json=data)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    if not verify_signature(body, signature):
        abort(400)

    events = json.loads(body).get("events", [])
    for event in events:
        if event.get("type") == "message" and event["message"].get("type") == "text":
            user_id = event["source"]["userId"]
            message_text = event["message"]["text"]
            reply_token = event["replyToken"]

            response_text = bot.get_response(user_id, message_text)
            reply_message(reply_token, response_text)

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
