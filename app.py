import os
import json
import hashlib
import hmac
import base64
import logging
import requests as req
from flask import Flask, request

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from bot import GrowthBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = GrowthBot()


def verify_signature(body, signature):
    """Verify LINE webhook signature"""
    if not LINE_CHANNEL_SECRET:
        logger.warning("LINE_CHANNEL_SECRET not set, skipping verification")
        return True
    if not signature:
        return False
    try:
        hash_value = hmac.new(
            LINE_CHANNEL_SECRET.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(hash_value).decode('utf-8')
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


def reply_message(reply_token, text):
    """Send reply message via LINE API"""
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }
    try:
        resp = req.post(url, headers=headers, json=data)
        logger.info(f"Reply status: {resp.status_code}")
    except Exception as e:
        logger.error(f"Reply error: {e}")


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    logger.info(f"Received webhook, body length: {len(body)}")

    # Verify signature - log but don't reject for now
    sig_valid = verify_signature(body, signature)
    if not sig_valid:
        logger.warning("Signature verification failed, but processing anyway")

    # Parse events
    try:
        data = json.loads(body)
        events = data.get("events", [])
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"JSON parse error: {e}")
        return "OK", 200

    # If no events (e.g., LINE Verify), just return OK
    if not events:
        logger.info("No events (possibly LINE Verify)")
        return "OK", 200

    for event in events:
        try:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                user_id = event["source"]["userId"]
                message_text = event["message"]["text"]
                reply_token = event["replyToken"]

                logger.info(f"Message from {user_id}: {message_text}")
                response_text = bot.get_response(user_id, message_text)
                logger.info(f"Response: {response_text}")
                reply_message(reply_token, response_text)
        except Exception as e:
            logger.error(f"Event processing error: {e}")

    return "OK", 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting bot on port {port}")
    app.run(host="0.0.0.0", port=port)
