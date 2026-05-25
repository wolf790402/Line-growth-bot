import jieba
import re

class IntentRecognizer:
    def __init__(self):
        # Load jieba dictionary if needed, or use default
        jieba.set_dictionary("dict.txt.big") # Using traditional Chinese dictionary

        self.intents = {
            "greeting": {
                "keywords": ["你好", "嗨", "哈囉", "早安", "午安", "晚安", "您好"],
                "patterns": []
            },
            "question_about_bot": {
                "keywords": ["你幾歲", "你是誰", "你叫什麼", "你的名字"],
                "patterns": [
                    r"你[是叫]?[什麼名]?[名字]?",
                    r"你[幾多]?[歲了]?"
                ]
            },
            "memory_query": {
                "keywords": ["記得", "忘記", "還記得", "還會"],
                "patterns": [
                    r"你[還]?[記得]?[我]?[喜歡愛]?[什麼]?",
                    r"你[還]?[記得]?[我]?[說過]?[什麼]?",
                    r"你[記得]?[我]?[叫]?[什麼]?"
                ]
            },
            "chatting": {
                "keywords": ["聊聊", "說說話", "閒聊", "故事", "心情"],
                "patterns": [
                    r"我[今天]?[很]?[開心難過生氣無聊]",
                    r"[分享]?[我的]?[心情]",
                    r"[說個]?[故事]"
                ]
            },
            "express_emotion": {
                "keywords": ["開心", "難過", "生氣", "無聊", "快樂", "沮喪", "興奮", "寂寞"],
                "patterns": [
                    r"我[很]?[開心難過生氣無聊快樂沮喪興奮寂寞]",
                    r"[好]?[開心難過生氣無聊快樂沮喪興奮寂寞]"
                ]
            },
            "teach_inform": {
                "keywords": ["我叫", "我喜歡", "今天發生", "告訴你", "跟你說"],
                "patterns": [
                    r"我叫(.+)",
                    r"我[喜歡愛]?[吃喝玩]?[(.+)]",
                    r"[記住]?[我]?[喜歡愛]?[吃喝玩]?[(.+)]",
                    r"[今天]?[發生了]?[(.+)]"
                ]
            },
            "correction": {
                "keywords": ["不對", "錯了", "不是這樣", "不正確", "搞錯了"],
                "patterns": []
            },
            "request_skill": {
                "keywords": ["辨識圖片", "寫程式", "翻譯", "計算"],
                "patterns": [
                    r"[幫我]?[辨識]?[這張]?[圖片]",
                    r"[幫我]?[寫個]?[程式]",
                    r"[幫我]?[翻譯]?[(.+)]"
                ]
            },
            "bot_status_query": {
                "keywords": ["你的等級", "你的心情", "你學會了什麼"],
                "patterns": [
                    r"你[的]?[等級]?[是多少]?",
                    r"你[的]?[心情]?[怎麼樣]?",
                    r"你[學會了]?[什麼]?"
                ]
            },
            "affirmation": {
                "keywords": ["好啊", "好的", "嗯嗯", "對啊", "沒錯", "可以"],
                "patterns": []
            },
            "negation": {
                "keywords": ["不要", "不好", "不行", "沒有"],
                "patterns": []
            }
        }

    def recognize_intent(self, message_text: str) -> str:
        # Pre-process message: segment words
        seg_list = jieba.cut(message_text, cut_all=False)
        segmented_message = " ".join(seg_list)

        # Prioritize correction intent
        for keyword in self.intents["correction"]["keywords"]:
            if keyword in message_text:
                return "correction"

        # Check for skill requests first, as they are usually explicit commands
        for intent_name, intent_data in self.intents.items():
            if intent_name == "correction": continue # Already checked
            if intent_name == "request_skill":
                for keyword in intent_data["keywords"]:
                    if keyword in message_text:
                        return intent_name
                for pattern in intent_data["patterns"]:
                    if re.search(pattern, message_text):
                        return intent_name

        # Check other intents by keywords and patterns
        for intent_name, intent_data in self.intents.items():
            if intent_name in ["correction", "request_skill"]: continue # Already checked
            for keyword in intent_data["keywords"]:
                if keyword in message_text:
                    return intent_name
            for pattern in intent_data["patterns"]:
                if re.search(pattern, message_text):
                    return intent_name

        return "chatting" # Default to chatting if no specific intent is recognized

    def extract_entities(self, message_text: str, intent: str) -> dict:
        entities = {}
        if intent == "teach_inform":
            name_match = re.search(r"我叫(.+)", message_text)
            if name_match: entities["user_name"] = name_match.group(1).strip()

            like_match = re.search(r"我[喜歡愛]?[吃喝玩]?[(.+)]", message_text)
            if like_match: entities["user_like"] = like_match.group(1).strip()

            remember_like_match = re.search(r"[記住]?[我]?[喜歡愛]?[吃喝玩]?[(.+)]", message_text)
            if remember_like_match: entities["user_like"] = remember_like_match.group(1).strip()

            event_match = re.search(r"[今天]?[發生了]?[(.+)]", message_text)
            if event_match: entities["event"] = event_match.group(1).strip()

        elif intent == "request_skill":
            skill_match = re.search(r"[幫我]?[辨識]?[這張]?[圖片]", message_text)
            if skill_match: entities["skill_name"] = "image_recognition"

            skill_match = re.search(r"[幫我]?[寫個]?[程式]", message_text)
            if skill_match: entities["skill_name"] = "code_generation"

            skill_match = re.search(r"[幫我]?[翻譯]?[(.+)]", message_text)
            if skill_match: entities["skill_name"] = "translation"; entities["content"] = skill_match.group(1).strip()

        return entities

# Download traditional Chinese dictionary for jieba
# This part should ideally be handled during setup or deployment
# For now, we'll assume dict.txt.big is available in the same directory
# import urllib.request
# try:
#     urllib.request.urlretrieve("https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big", "dict.txt.big")
# except Exception as e:
#     print(f"Could not download dict.txt.big: {e}. Please ensure it's available.")
