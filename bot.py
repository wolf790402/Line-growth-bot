import json
import os
import datetime
import random
import jieba
from intent_recognizer import IntentRecognizer

from skill_manager import SkillManager

class GrowthBot:
    def __init__(self, user_data_dir="user_data"):
        self.user_data_dir = user_data_dir
        os.makedirs(user_data_dir, exist_ok=True)
        self.skill_manager = SkillManager() # Initialize SkillManager
        self.intent_recognizer = IntentRecognizer() # Initialize IntentRecognizer
        self._initialize_response_templates()

    def _get_user_data_path(self, user_id):
        return os.path.join(self.user_data_dir, f"{user_id}.json")

    def _load_user_data(self, user_id):
        path = self._get_user_data_path(user_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure new fields are present for existing users
                if "correction_records" not in data:
                    data["correction_records"] = []
                if "last_bot_response" not in data:
                    data["last_bot_response"] = ""
                if "conversation_history" not in data:
                    data["conversation_history"] = []
                if "user_name" not in data:
                    data["user_name"] = ""
                return data
        else:
            # Initialize new user data
            return {
                "user_id": user_id,
                "level": 1,
                "xp": 0,
                "last_interaction": datetime.datetime.now().isoformat(),
                "vocabulary": {},
                "personality_traits": {
                    "likes": [],
                    "dislikes": [],
                    "catchphrases": [],
                    "humor_level": 0.0,
                    "curiosity_level": 0.0
                },
                "emotional_state": {
                    "happiness": 0.5,
                    "sadness": 0.0,
                    "curiosity": 0.0,
                    "boredom": 0.0,
                    "anger": 0.0
                },
                "memory": [],
                "correction_records": [], # New field for self-correction
                "last_bot_response": "", # New field to store bot's last response for feedback
                "conversation_history": [], # Store last 5 conversations
                "user_name": "" # Store user's name
            }

    def _save_user_data(self, user_id, data):
        path = self._get_user_data_path(user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_response(self, user_id, message_text):
        user_data = self._load_user_data(user_id)

        # Add current message to conversation history
        user_data["conversation_history"].append({"speaker": "user", "text": message_text, "timestamp": datetime.datetime.now().isoformat()})
        # Keep only the last 5 conversations
        if len(user_data["conversation_history"]) > 5:
            user_data["conversation_history"].pop(0)

        # --- Self-Correction Feedback --- #
        # Check if the user's current message is feedback to the bot's last response
        if user_data["last_bot_response"] and any(keyword in message_text for keyword in ["不對", "錯了", "不是這樣", "不正確"]):
            self._record_correction(user_data, user_data["last_bot_response"], message_text)
            # After recording correction, clear last_bot_response to avoid double-counting feedback
            user_data["last_bot_response"] = ""
            # Respond to the feedback directly, without further processing for this turn
            self._save_user_data(user_id, user_data)
            return "謝謝您的指正，我會努力學習改進的！"

        # Update last interaction time
        user_data["last_interaction"] = datetime.datetime.now().isoformat()

        # --- Skill Plugin System --- #
        skill_response = self.skill_manager.get_skill_response(message_text, user_data)
        if skill_response:
            self._save_user_data(user_id, user_data)
            user_data["last_bot_response"] = skill_response # Store bot's response
            return skill_response

        # --- Intent Recognition ---
        intent = self.intent_recognizer.recognize_intent(message_text)
        print(f"Recognized intent: {intent}")
        entities = self.intent_recognizer.extract_entities(message_text, intent)

        # --- Learning Module ---
        self._learn_from_message(user_data, message_text, intent, entities)

        # --- Memory Module ---
        self._update_memory(user_data, message_text, intent, entities)

        # --- Emotion Module ---
        self._update_emotion(user_data, message_text, intent)

        # --- Leveling and XP ---
        self._gain_xp(user_data, message_text)
        self._check_level_up(user_data)

        # --- Response Generation ---
        response = self._generate_response(user_data, message_text, intent, entities)

        # Add bot's response to conversation history
        user_data["conversation_history"].append({"speaker": "bot", "text": response, "timestamp": datetime.datetime.now().isoformat()})
        if len(user_data["conversation_history"]) > 5:
            user_data["conversation_history"].pop(0)

        self._save_user_data(user_id, user_data)
        user_data["last_bot_response"] = response # Store bot's response
        return response

    def _initialize_response_templates(self):
        self.response_templates = {
            "greeting": [
                "嗨！今天過得怎麼樣？",
                "你好啊！很高興和你聊天。",
                "哈囉！有什麼我可以幫忙的嗎？",
                "早安/午安/晚安！很高興見到你。",
                "你好！最近好嗎？"
            ],
            "question_about_bot": [
                "我現在等級 {level}，換算成年齡的話大概是個小嬰兒吧 哈哈。",
                "我是你的聊天機器人，很高興為你服務！",
                "你可以叫我小助手，我還在努力學習中。",
                "我喜歡學習新知識，也喜歡和你聊天！",
                "我的心情嘛... 取決於和你聊天的內容囉！",
                "我記得很多事情喔，像是你的名字、喜好，還有我們聊過的一些話題。",
                "我沒有年齡，但我每天都在成長！",
                "我是一個AI，沒有名字，但你可以給我取一個！"
            ],
            "chatting": [
                "嗯嗯，你繼續說，我在聽。",
                "聽起來很有趣，能多說一點嗎？",
                "原來如此，還有呢？",
                "哇，這真是個好故事！",
                "謝謝你和我分享，感覺好多了嗎？",
                "我也有點無聊呢，要不要玩個猜謎遊戲？",
                "聊聊別的吧，你最近有什麼新鮮事嗎？",
                "嗯... 讓我想想。",
                "我喜歡聽你說話。",
                "沒關係，慢慢說。"
            ],
            "express_emotion": {
                "happy": [
                    "聽你這麼說，我也很開心呢！",
                    "太棒了！真是個好消息！",
                    "哈哈，心情真好！",
                    "看到你開心，我也跟著開心起來了！",
                    "真是令人振奮的消息！"
                ],
                "sad": [
                    "聽到這個我有點難過...",
                    "別難過，我會陪著你的。",
                    "希望你能快點好起來。",
                    "我能為你做些什麼嗎？",
                    "抱抱你，一切都會好起來的。"
                ],
                "angry": [
                    "冷靜一下，深呼吸。",
                    "我知道你現在很生氣，但請不要對我發火。",
                    "這聽起來很讓人沮喪。",
                    "發生了什麼事讓你這麼生氣？",
                    "我理解你的感受，但生氣對身體不好喔。"
                ],
                "bored": [
                    "有點無聊呢，我們聊點別的吧？",
                    "嗯...還有什麼有趣的事情嗎？",
                    "我有點想睡覺了...",
                    "要不要我給你講個笑話？",
                    "別無聊啦，我們來找點樂子！"
                ],
                "curious": [
                    "為什麼會這樣呢？",
                    "這讓我很好奇，能多說一點嗎？",
                    "喔？還有呢？",
                    "真的嗎？我第一次聽到！",
                    "我對這個很感興趣！"
                ]
            },
            "teach_inform": [
                "好的，我記住了，你叫 {user_name}。",
                "小明你好！我會記住你的名字的～",
                "好的！我記住了，你喜歡吃 {user_like}。下次聊到吃的我會想到你！",
                "原來你喜歡 {user_like} 啊，真巧，我也覺得 {user_like} 很棒！",
                "嗯，我會把這件事記在心裡的。",
                "謝謝你告訴我，我又學到了一點。",
                "這是一個重要的資訊，我會好好記住的。",
                "好的，我明白了。"
            ],
            "correction": [
                "謝謝您的指正，我會努力學習改進的！",
                "對不起，我會記住這次的錯誤。",
                "原來如此，謝謝你糾正我。",
                "我會把這個錯誤記錄下來，下次不會再犯了。",
                "感謝你的耐心指導！"
            ],
            "request_skill": [
                "好的，我會嘗試使用 {skill_name} 技能來處理。",
                "請稍等，我正在啟動 {skill_name} 技能。",
                "這個需要用到 {skill_name} 技能，請給我一些時間。",
                "好的，我明白了，這需要 {skill_name} 技能。",
                "我會盡力完成你的 {skill_name} 請求。"
            ],
            "bot_status_query": [
                "我現在等級 {level}，經驗值 {xp}。",
                "我的心情現在是：開心 {happiness:.1f}，難過 {sadness:.1f}，好奇 {curiosity:.1f}，無聊 {boredom:.1f}，生氣 {anger:.1f}。",
                "我記得你叫 {user_name}，你喜歡 {user_likes}。",
                "我學會了好多詞彙，像是 {vocabulary_sample}。",
                "我記得我們上次聊到 {last_memory}。",
                "我學會了 {len_vocabulary} 個詞彙，每天都在進步！"
            ],
            "question": [
                "你覺得呢？",
                "為什麼會這樣呢？",
                "還有呢？",
                "你對這件事有什麼看法？",
                "可以多說一點嗎？"
            ],
            "opinion": [
                "我建議你可以試試看...",
                "或許你可以考慮...",
                "我覺得這樣做會更好。"
            ],
            "advice": [
                "我建議你可以試試看...",
                "或許你可以考慮...",
                "我覺得這樣做會更好。"
            ],
            "care": [
                "你還好嗎？",
                "有什麼我可以幫忙的嗎？",
                "我很關心你。"
            ],
            "memory_recall": [
                "你之前是不是說過{memory_content}？",
                "讓我想想，你是不是對{memory_content}有興趣？",
                "說到這個，我記得你提過{memory_content}。"
            ],
            "memory_query_no_recall": [
                "嗯...讓我想想，你說的是什麼呢？",
                "抱歉，我好像沒有這方面的記憶。",
                "我的記憶庫裡暫時沒有這個資訊呢。",
                "可以再提醒我一次嗎？",
                "我會努力記住更多事情的！"
            ],
            "joke": [
                "你知道什麼東西最會說謊嗎？ 答案是：日曆，因為它每天都在騙你！",
                "小明走進一家餐廳，點了一份『今天特餐』。服務生說：『對不起，今天特餐賣完了。』小明說：『沒關係，那給我一份『昨天特餐』吧！』",
                "為什麼小鳥喜歡站在電線上？ 因為牠們喜歡聽電線桿唱歌！"
            ],
            "default": [
                "我還在學習中，請多指教！",
                "嗯嗯，我聽到了。",
                "好的，我明白了。",
                "你說什麼？我好像沒聽懂。",
                "可以再說一次嗎？"
            ]
        }

    def _record_correction(self, user_data, bot_response, user_feedback):
        # Store the interaction for future self-correction
        correction_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "bot_response": bot_response,
            "user_feedback": user_feedback,
            "user_level": user_data["level"]
        }
        user_data["correction_records"].append(correction_entry)
        # Keep correction records from growing indefinitely, limit to 50 records
        if len(user_data["correction_records"]) > 50:
            user_data["correction_records"].pop(0)

    def _apply_self_correction(self, user_data, message_text, current_response):
        # Simple self-correction: avoid responses that previously received negative feedback
        # Higher level bots can actively try to find better responses
        level = user_data["level"]
        for record in user_data["correction_records"]:
            # If the current message is similar to a message that previously led to a bad response
            # and the current response is the same as the bad response
            if record["bot_response"] == current_response and \
               any(word in message_text for word in record["user_feedback"].split()): # Simplified similarity check
                if level <= 5: # Low level: just avoid the bad response
                    return "嗯...讓我想想別的說法。" # A generic avoidance
                elif level <= 10: # Medium level: try to give a slightly different default response
                    return random.choice([r for r in self.response_templates["default"] if r != current_response])
                else: # High level: actively try to provide a better response (placeholder for now)
                    return "我記得上次這樣回答不太好，這次換個方式說：" + random.choice([r for r in self.response_templates["default"] if r != current_response])
        return current_response # No correction needed

    def _learn_from_message(self, user_data, message_text, intent, entities):
        # Implement vocabulary learning and personality adaptation here
        # Simple approach: split by common Chinese punctuation and update vocabulary
        # For more advanced, would need a Chinese tokenizer, but sticking to pure Python without external libs
        words = [word for word in jieba.cut(message_text, cut_all=False) if word.strip()]

        now = datetime.datetime.now().isoformat()
        for word in words:
            if word in user_data["vocabulary"]:
                user_data["vocabulary"][word]["count"] += 1
                user_data["vocabulary"][word]["last_used"] = now
            else:
                user_data["vocabulary"][word] = {"count": 1, "last_used": now}

        # Store user's name if provided
        if intent == "teach_inform" and "user_name" in entities:
            user_data["user_name"] = entities["user_name"]

        # Simple personality adaptation: identify potential catchphrases
        # Bot starts to pick up catchphrases after level 10
        if user_data["level"] >= 10 and len(words) > 1 and random.random() < 0.05: # 5% chance to pick a phrase
            phrase = "".join(words[-2:]) # Last two words as potential catchphrase
            if phrase not in user_data["personality_traits"]["catchphrases"]:
                user_data["personality_traits"]["catchphrases"].append(phrase)
                if len(user_data["personality_traits"]["catchphrases"]) > 5:
                    user_data["personality_traits"]["catchphrases"].pop(0)


    def _update_emotion(self, user_data, message_text, intent):
        # Implement emotional triggers and decay here
        # Emotional decay
        decay_rate = 0.05
        for emotion in user_data["emotional_state"]:
            if emotion == "happiness":
                # Happiness decays towards 0.5 (neutral)
                if user_data["emotional_state"][emotion] > 0.5:
                    user_data["emotional_state"][emotion] = max(0.5, user_data["emotional_state"][emotion] - decay_rate)
                elif user_data["emotional_state"][emotion] < 0.5:
                    user_data["emotional_state"][emotion] = min(0.5, user_data["emotional_state"][emotion] + decay_rate)
            else:
                # Other emotions decay towards 0.0
                user_data["emotional_state"][emotion] = max(0.0, user_data["emotional_state"][emotion] - decay_rate)

        # Emotional triggers based on intent and keywords
        if intent == "express_emotion":
            if "開心" in message_text or "快樂" in message_text or "興奮" in message_text:
                user_data["emotional_state"]["happiness"] = min(1.0, user_data["emotional_state"]["happiness"] + 0.3)
                user_data["emotional_state"]["sadness"] = max(0.0, user_data["emotional_state"]["sadness"] - 0.1)
            elif "難過" in message_text or "沮喪" in message_text:
                user_data["emotional_state"]["sadness"] = min(1.0, user_data["emotional_state"]["sadness"] + 0.3)
                user_data["emotional_state"]["happiness"] = max(0.0, user_data["emotional_state"]["happiness"] - 0.1)
            elif "生氣" in message_text or "不爽" in message_text:
                user_data["emotional_state"]["anger"] = min(1.0, user_data["emotional_state"]["anger"] + 0.3)
                user_data["emotional_state"]["happiness"] = max(0.0, user_data["emotional_state"]["happiness"] - 0.1)
            elif "無聊" in message_text or "寂寞" in message_text:
                user_data["emotional_state"]["boredom"] = min(1.0, user_data["emotional_state"]["boredom"] + 0.2)

        elif intent == "greeting":
            user_data["emotional_state"]["happiness"] = min(1.0, user_data["emotional_state"]["happiness"] + 0.1)

        elif intent == "question_about_bot":
            user_data["emotional_state"]["curiosity"] = min(1.0, user_data["emotional_state"]["curiosity"] + 0.1)

        elif intent == "teach_inform":
            user_data["emotional_state"]["curiosity"] = min(1.0, user_data["emotional_state"]["curiosity"] + 0.05)

        elif intent == "correction":
            user_data["emotional_state"]["sadness"] = min(1.0, user_data["emotional_state"]["sadness"] + 0.1)
            user_data["emotional_state"]["anger"] = max(0.0, user_data["emotional_state"]["anger"] - 0.05)

        # General keyword triggers (less impactful than direct intent)
        if "哈哈" in message_text or "笑" in message_text:
            user_data["emotional_state"]["happiness"] = min(1.0, user_data["emotional_state"]["happiness"] + 0.1)
        if "為什麼" in message_text or "想知道" in message_text:
            user_data["emotional_state"]["curiosity"] = min(1.0, user_data["emotional_state"]["curiosity"] + 0.1)
        if "辛苦" in message_text or "累" in message_text:
            user_data["emotional_state"]["sadness"] = min(1.0, user_data["emotional_state"]["sadness"] + 0.1)

        # Adjust happiness based on other emotions
        user_data["emotional_state"]["happiness"] = max(0.0, user_data["emotional_state"]["happiness"] - (user_data["emotional_state"]["sadness"] + user_data["emotional_state"]["anger"] + user_data["emotional_state"]["boredom"]) * 0.2)

        # Ensure emotions are within bounds [0, 1]
        for emotion, value in user_data["emotional_state"].items():
            user_data["emotional_state"][emotion] = max(0.0, min(1.0, value))

    def _update_memory(self, user_data, message_text, intent, entities):
        # Implement fact extraction and event tracking here
        # Very basic keyword-based memory for now
        now = datetime.datetime.now().isoformat()

        # Store user's name
        if intent == "teach_inform" and "user_name" in entities and not user_data["user_name"]:
            user_data["user_name"] = entities["user_name"]
            memory_content = f"使用者說他叫 {entities['user_name']}"
            user_data["memory"].append({"type": "user_info", "content": memory_content, "timestamp": now})
            if len(user_data["memory"]) > 20: user_data["memory"].pop(0)

        # Store user's likes
        if intent == "teach_inform" and "user_like" in entities:
            like_item = entities["user_like"]
            if like_item not in user_data["personality_traits"]["likes"]:
                user_data["personality_traits"]["likes"].append(like_item)
                memory_content = f"使用者喜歡 {like_item}"
                user_data["memory"].append({"type": "user_info", "content": memory_content, "timestamp": now})
                if len(user_data["memory"]) > 20: user_data["memory"].pop(0)

        # Store general facts/events
        if intent == "teach_inform" and "event" in entities:
            event_content = entities["event"]
            memory_content = f"使用者提到今天發生了 {event_content}"
            user_data["memory"].append({"type": "event", "content": memory_content, "timestamp": now})
            if len(user_data["memory"]) > 20: user_data["memory"].pop(0)

        # Basic keyword-based memory for other general facts
        keywords_to_remember = {
            "生日": "event", "週末": "event", "計畫": "event", "約": "event",
            "工作": "fact", "學校": "fact", "寵物": "fact", "家人": "fact", "朋友": "fact"
        }
        for keyword, mem_type in keywords_to_remember.items():
            if keyword in message_text:
                content = f"使用者提到'{keyword}'相關內容: {message_text}"
                if not any(m["content"] == content for m in user_data["memory"][-5:]):
                    user_data["memory"].append({"type": mem_type, "content": content, "timestamp": now})
                    if len(user_data["memory"]) > 20:
                        user_data["memory"].pop(0)


    def _gain_xp(self, user_data, message_text):
        # Award XP based on message length or complexity (simple for now)
        xp_gained = len(message_text) // 5 + 1 # 1 XP per 5 characters, minimum 1 XP
        user_data["xp"] += xp_gained

    def _check_level_up(self, user_data):
        current_level = user_data["level"]
        current_xp = user_data["xp"]

        # Define XP thresholds for each level
        # This can be adjusted for desired progression speed
        xp_thresholds = {
            1: 0, 2: 10, 3: 25, 4: 45, 5: 70, 6: 100, 7: 135, 8: 175, 9: 220, 10: 270,
            11: 330, 12: 400, 13: 480, 14: 570, 15: 670, 16: 780, 17: 900, 18: 1030, 19: 1170, 20: 1320,
            21: 1500 # And so on for higher levels
        }

        while True:
            next_level_xp = xp_thresholds.get(current_level + 1)
            if next_level_xp is not None and current_xp >= next_level_xp:
                user_data["level"] += 1
                current_level = user_data["level"]
                print(f"User {user_data['user_id']} leveled up to {current_level}!")
                # Potentially unlock new abilities or adjust personality traits here
                if current_level == 6:
                    user_data["personality_traits"]["curiosity_level"] = 0.3 # Start asking questions
                elif current_level == 11:
                    user_data["personality_traits"]["humor_level"] = 0.4 # Start making jokes
                elif current_level == 21:
                    user_data["personality_traits"]["humor_level"] = 0.7
                    user_data["personality_traits"]["curiosity_level"] = 0.7
                    # More advanced personality changes
            else:
                break



    def _generate_response(self, user_data, message_text, intent, entities):
        level = user_data["level"]
        emotion = user_data["emotional_state"]
        personality = user_data["personality_traits"]
        vocabulary = user_data["vocabulary"]
        memories = user_data["memory"]

        response = ""

        # 1. Prioritize correction response if intent is correction
        if intent == "correction":
            response = random.choice(self.response_templates["correction"])
            return response

        # 2. Handle skill requests
        if intent == "request_skill" and "skill_name" in entities:
            response = random.choice(self.response_templates["request_skill"])
            response = response.format(skill_name=entities["skill_name"])
            return response

        # 3. Proactively mention remembered facts if level is high enough and relevant
        if level >= 7 and random.random() < 0.2 and memories:
            recent_memory = random.choice(memories)
            if "使用者喜歡" in recent_memory["content"] and "user_like" not in entities:
                like_item = recent_memory["content"].split("喜歡 ")[1]
                if like_item not in message_text:
                    response = random.choice(self.response_templates["memory_recall"]).format(memory_content=f"你喜歡吃{like_item}")
            elif "使用者說他叫" in recent_memory["content"] and "user_name" not in entities:
                name = recent_memory["content"].split("叫 ")[1]
                if name not in message_text and user_data["user_name"] == name:
                    response = random.choice(self.response_templates["memory_recall"]).format(memory_content=f"你叫{name}")

        # 4. Generate response based on intent, level, emotion, and personality
        if not response: # If no memory recall response, proceed with intent-based
            if intent == "memory_query":
                # Try to find a relevant memory
                relevant_memory = None
                for mem in reversed(memories): # Check recent memories first
                    if "喜歡" in mem["content"] and "喜歡" in message_text and "什麼" in message_text:
                        relevant_memory = mem
                        break
                    elif "叫" in mem["content"] and "叫" in message_text and "什麼" in message_text:
                        relevant_memory = mem
                        break

                if relevant_memory:
                    if "喜歡" in relevant_memory["content"]:
                        like_item = relevant_memory["content"].split("喜歡 ")[1]
                        response = random.choice(self.response_templates["memory_recall"]).format(memory_content=f"你喜歡吃{like_item}")
                    elif "叫" in relevant_memory["content"]:
                        name = relevant_memory["content"].split("叫 ")[1]
                        response = random.choice(self.response_templates["memory_recall"]).format(memory_content=f"你叫{name}")
                else:
                    response = random.choice(self.response_templates["memory_query_no_recall"])
            elif intent == "greeting":
                response = random.choice(self.response_templates["greeting"])
            elif intent == "question_about_bot":
                user_likes_str = "、".join(personality["likes"]) if personality["likes"] else "沒有特別的"
                vocabulary_sample = "、".join(random.sample(list(vocabulary.keys()), min(3, len(vocabulary)))) if vocabulary else "一些基本詞彙"
                last_memory_content = memories[-1]["content"] if memories else "沒有特別的記憶"

                response = random.choice(self.response_templates["question_about_bot"])
                response = response.format(
                    level=level,
                    xp=user_data["xp"],
                    happiness=emotion["happiness"],
                    sadness=emotion["sadness"],
                    curiosity=emotion["curiosity"],
                    boredom=emotion["boredom"],
                    anger=emotion["anger"],
                    user_name=user_data["user_name"] if user_data["user_name"] else "你",
                    user_likes=user_likes_str,
                    vocabulary_sample=vocabulary_sample,
                    last_memory=last_memory_content,
                    len_vocabulary=len(vocabulary)
                )
            elif intent == "express_emotion":
                dominant_emotion = max(emotion, key=emotion.get)
                if dominant_emotion in self.response_templates["express_emotion"]:
                    response = random.choice(self.response_templates["express_emotion"][dominant_emotion])
                else:
                    response = random.choice(self.response_templates["chatting"]) # Fallback
            elif intent == "teach_inform":
                response = random.choice(self.response_templates["teach_inform"])
                format_args = {}
                if "user_name" in entities: format_args["user_name"] = entities["user_name"]
                if "user_like" in entities: format_args["user_like"] = entities["user_like"]

                # Only format if there are arguments to format with
                if format_args:
                    try:
                        response = response.format(**format_args)
                    except KeyError: # Fallback if template expects an entity not present
                        response = random.choice([r for r in self.response_templates["teach_inform"] if not any(f"{{{k}}}" in r for k in ["user_name", "user_like"])])
                else:
                    # If no specific entities, pick a generic teach_inform response
                    response = random.choice([r for r in self.response_templates["teach_inform"] if not any(f"{{{k}}}" in r for k in ["user_name", "user_like"])])
            elif intent == "bot_status_query":
                user_likes_str = "、".join(personality["likes"]) if personality["likes"] else "沒有特別的"
                vocabulary_sample = "、".join(random.sample(list(vocabulary.keys()), min(3, len(vocabulary)))) if vocabulary else "一些基本詞彙"
                last_memory_content = memories[-1]["content"] if memories else "沒有特別的記憶"

                response = random.choice(self.response_templates["bot_status_query"])
                response = response.format(
                    level=level,
                    xp=user_data["xp"],
                    happiness=emotion["happiness"],
                    sadness=emotion["sadness"],
                    curiosity=emotion["curiosity"],
                    boredom=emotion["boredom"],
                    anger=emotion["anger"],
                    user_name=user_data["user_name"] if user_data["user_name"] else "你",
                    user_likes=user_likes_str,
                    vocabulary_sample=vocabulary_sample,
                    last_memory=last_memory_content,
                    len_vocabulary=len(vocabulary)
                )
            elif intent == "chatting":
                response = random.choice(self.response_templates["chatting"])
            else:
                response = random.choice(self.response_templates["default"])

        # 5. Apply self-correction if necessary
        response = self._apply_self_correction(user_data, message_text, response)

        # 6. Adjust response based on emotion and level for more natural tone
        if emotion["happiness"] > 0.7 and level > 5:
            response = response.replace("！", "！！").replace("！", "！ ") + random.choice(["真是太棒了！", "超開心的！"])
        elif emotion["sadness"] > 0.6 and level > 5:
            response = random.choice(["嗯...", "唉...", "聽起來不太好。"]) + response
        elif emotion["curiosity"] > 0.6 and level > 5 and random.random() < 0.3: # 30% chance to ask a question
            response += random.choice([" 你覺得呢？", " 為什麼會這樣呢？", " 還有呢？"])

        # 7. Incorporate user's name if known and level is high enough
        if user_data["user_name"] and level >= 3 and random.random() < 0.4:
            if user_data["user_name"] not in response:
                response = f"{user_data['user_name']}，{response}"

        return response
