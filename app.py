import os
import json
import hashlib
import hmac
import base64
import logging
import random
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
            if event.get("type") == "message":
                user_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                msg_type = event["message"].get("type")

                if msg_type == "text":
                    message_text = event["message"]["text"]
                    logger.info(f"Message from {user_id}: {message_text}")
                    response_text = bot.get_response(user_id, message_text)
                    logger.info(f"Response: {response_text}")
                    reply_message(reply_token, response_text)

                elif msg_type == "sticker":
                    sticker_responses = [
                        "哈哈，好可愛的貼圖！",
                        "收到你的貼圖了～",
                        "我也想傳貼圖給你，可惜我還不會 😆",
                        "這個貼圖好有趣！",
                        "貼圖收到！你今天心情不錯吧？",
                        "哈哈哈，我喜歡這個貼圖！",
                        "雖然我看不太懂貼圖，但感覺你很開心～",
                        "好想學會用貼圖回你喔！",
                    ]
                    reply_message(reply_token, random.choice(sticker_responses))

                elif msg_type == "image":
                    image_responses = [
                        "哇，你傳了一張圖片給我！可惜我現在還看不懂圖片。",
                        "收到圖片了！等我學會 OCR 技能就能看懂了。",
                        "好想看懂你傳的圖片喔，再等我升級一下！",
                        "圖片收到～雖然我現在還是個看不懂圖的小笨蛋。",
                    ]
                    reply_message(reply_token, random.choice(image_responses))

                elif msg_type == "video":
                    video_responses = [
                        "你傳了影片給我！可惜我現在還不會看影片。",
                        "影片收到了，等我等級更高就能處理影片了！",
                        "哇是影片！我好期待學會看影片的那天。",
                    ]
                    reply_message(reply_token, random.choice(video_responses))

                elif msg_type == "audio":
                    audio_responses = [
                        "你傳了語音給我！可惜我現在還聽不懂。",
                        "語音收到了～等我學會聽力技能就能聽懂了！",
                        "好想聽懂你說什麼喔，再給我一點時間成長！",
                    ]
                    reply_message(reply_token, random.choice(audio_responses))

                else:
                    reply_message(reply_token, "我收到了，但這種訊息我還看不太懂，多跟我聊天讓我成長吧！")

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
