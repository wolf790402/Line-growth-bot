import json
import os
import datetime
import random

from skill_manager import SkillManager

class GrowthBot:
    def __init__(self, user_data_dir="user_data"):
        self.user_data_dir = user_data_dir
        os.makedirs(user_data_dir, exist_ok=True)
        self.skill_manager = SkillManager() # Initialize SkillManager

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
                if "last_bot_response" not in data: # To track for self-correction feedback
                    data["last_bot_response"] = ""
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
                "last_bot_response": "" # New field to store bot's last response for feedback
            }

    def _save_user_data(self, user_id, data):
        path = self._get_user_data_path(user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_response(self, user_id, message_text):
        user_data = self._load_user_data(user_id)

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

        # --- Learning Module (Placeholder) ---
        self._learn_from_message(user_data, message_text)

        # --- Memory Module (Placeholder) ---
        self._update_memory(user_data, message_text)

        # --- Emotion Module (Placeholder) ---
        self._update_emotion(user_data, message_text)

        # --- Leveling and XP (Placeholder) ---
        self._gain_xp(user_data, message_text)
        self._check_level_up(user_data)

        # --- Response Generation (Placeholder) ---
        response = self._generate_response(user_data, message_text)

        self._save_user_data(user_id, user_data)
        user_data["last_bot_response"] = response # Store bot's response
        return response

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

    def _learn_from_message(self, user_data, message_text):
        # Implement vocabulary learning and personality adaptation here
        # Simple approach: split by common Chinese punctuation and update vocabulary
        # For more advanced, would need a Chinese tokenizer, but sticking to pure Python without external libs
        words = []
        # A very basic tokenization by common Chinese punctuation
        for punc in ['，', '。', '？', '！', '、', '；', '：', '「', '」', '『', '』', '（', '）', '《', '》', '—', '～', ' ', '\n']:
            message_text = message_text.replace(punc, ' ')
        words = [word.strip() for word in message_text.split() if word.strip()]

        now = datetime.datetime.now().isoformat()
        for word in words:
            if word in user_data["vocabulary"]:
                user_data["vocabulary"][word]["count"] += 1
                user_data["vocabulary"][word]["last_used"] = now
            else:
                user_data["vocabulary"][word] = {"count": 1, "last_used": now}

        # Simple personality adaptation: identify potential catchphrases
        # Bot starts to pick up catchphrases after level 10
        if user_data["level"] >= 10 and len(words) > 1 and random.random() < 0.05: # 5% chance to pick a phrase
            phrase = "".join(words[-2:]) # Last two words as potential catchphrase
            if phrase not in user_data["personality_traits"]["catchphrases"]:
                user_data["personality_traits"]["catchphrases"].append(phrase)
                if len(user_data["personality_traits"]["catchphrases"]) > 5:
                    user_data["personality_traits"]["catchphrases"].pop(0)


    def _update_emotion(self, user_data, message_text):
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

        # Emotional triggers (simplified keyword-based)
        if "開心" in message_text or "高興" in message_text or "哈哈" in message_text:
            user_data["emotional_state"]["happiness"] = min(1.0, user_data["emotional_state"]["happiness"] + 0.2)
            user_data["emotional_state"]["sadness"] = max(0.0, user_data["emotional_state"]["sadness"] - 0.1)
        if "難過" in message_text or "不開心" in message_text or "哭" in message_text:
            user_data["emotional_state"]["sadness"] = min(1.0, user_data["emotional_state"]["sadness"] + 0.2)
            user_data["emotional_state"]["happiness"] = max(0.0, user_data["emotional_state"]["happiness"] - 0.1)
        if "為什麼" in message_text or "好奇" in message_text or "想知道" in message_text:
            user_data["emotional_state"]["curiosity"] = min(1.0, user_data["emotional_state"]["curiosity"] + 0.15)
        if "無聊" in message_text or "沒事" in message_text:
            user_data["emotional_state"]["boredom"] = min(1.0, user_data["emotional_state"]["boredom"] + 0.15)
        if "生氣" in message_text or "氣死" in message_text or "不爽" in message_text:
            user_data["emotional_state"]["anger"] = min(1.0, user_data["emotional_state"]["anger"] + 0.2)
            user_data["emotional_state"]["happiness"] = max(0.0, user_data["emotional_state"]["happiness"] - 0.1)

        # Ensure emotions are within bounds [0, 1]
        for emotion, value in user_data["emotional_state"].items():
            user_data["emotional_state"][emotion] = max(0.0, min(1.0, value))

    def _update_memory(self, user_data, message_text):
        # Implement fact extraction and event tracking here
        # Very basic keyword-based memory for now
        keywords_to_remember = {
            "喜歡": "likes", "愛": "likes", "討厭": "dislikes", "不喜歡": "dislikes",
            "生日": "event", "週末": "event", "計畫": "event", "約": "event",
            "工作": "fact", "學校": "fact", "寵物": "fact", "家人": "fact", "朋友": "fact"
        }
        now = datetime.datetime.now().isoformat()
        for keyword, mem_type in keywords_to_remember.items():
            if keyword in message_text:
                content = f"使用者提到'{keyword}'相關內容: {message_text}"
                # Avoid duplicate memories for the exact same content within a short period
                # Check last 5 memories to prevent immediate duplicates
                if not any(m["content"] == content for m in user_data["memory"][-5:]):
                    user_data["memory"].append({"type": mem_type, "content": content, "timestamp": now})
                    # Keep memory list from growing indefinitely, limit to 20 memories
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

    def _generate_response(self, user_data, message_text):
        level = user_data["level"]
        emotion = user_data["emotional_state"]
        personality = user_data["personality_traits"]
        vocabulary = user_data["vocabulary"]
        memories = user_data["memory"]

        response_templates = {
            "default": [
                "我還在學習中，請多指教！",
                "嗯嗯，我聽到了。",
                "好的，我明白了。"
            ],
            "happy": [
                "聽你這麼說，我也很開心呢！",
                "太棒了！真是個好消息！",
                "哈哈，心情真好！"
            ],
            "sad": [
                "聽到這個我有點難過...",
                "別難過，我會陪著你的。",
                "希望你能快點好起來。"
            ],
            "curious": [
                "為什麼會這樣呢？",
                "這讓我很好奇，能多說一點嗎？",
                "喔？還有呢？"
            ],
            "bored": [
                "有點無聊呢，我們聊點別的吧？",
                "嗯...還有什麼有趣的事情嗎？",
                "我有點想睡覺了..."
            ],
            "angry": [
                "冷靜一下，深呼吸。",
                "我知道你現在很生氣，但請不要對我發火。",
                "這聽起來很讓人沮喪。"
            ],
            "question": [
                "你覺得呢？",
                "那你打算怎麼辦？",
                "你對這件事有什麼看法？"
            ],
            "opinion": [
                "我覺得...",
                "我不太同意...",
                "我的看法是..."
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
            "joke": [
                "你知道什麼東西最會說謊嗎？ 答案是：日曆，因為它每天都在騙你！",
                "小明走進一家餐廳，點了一份『今天特餐』。服務生說：『對不起，今天特餐賣完了。』小明說：『沒關係，那給我一份『昨天特餐』吧！』",
                "為什麼小鳥喜歡站在電線上？ 因為牠們喜歡聽電線桿唱歌！"
            ]
        }
        self.response_templates = response_templates # Make it accessible for self-correction

        response = random.choice(response_templates["default"])

        # Apply self-correction before generating a new response
        response = self._apply_self_correction(user_data, message_text, response)

        # Level 1-5: Simple responses, vocabulary imitation
        if level <= 5:
            # Try to imitate user's common words
            if vocabulary:
                common_words = sorted(vocabulary.items(), key=lambda item: item[1]["count"], reverse=True)
                for word, data in common_words:
                    if word in message_text and random.random() < 0.3: # 30% chance to use a learned word
                        response = f"你說的'{word}'，我記住了。" + random.choice(response_templates["default"])
                        break

        # Level 6-10: Ask questions, proactively mention memories
        elif 6 <= level <= 10:
            if random.random() < personality["curiosity_level"] and emotion["curiosity"] > 0.3:
                response = random.choice(response_templates["question"])
            elif memories and random.random() < 0.2: # 20% chance to recall memory
                recent_memory = random.choice(memories[-5:]) # Pick from last 5 memories
                response = random.choice(response_templates["memory_recall"]).format(memory_content=recent_memory["content"])
            else:
                response = random.choice(response_templates["default"])

        # Level 11-20: Jokes, catchphrases, express opinions
        elif 11 <= level <= 20:
            if random.random() < personality["humor_level"] and emotion["happiness"] > 0.6:
                response = random.choice(response_templates["joke"])
            elif random.random() < 0.3: # 30% chance to express opinion
                response = random.choice(response_templates["opinion"])
            elif personality["catchphrases"] and random.random() < 0.3:
                response = random.choice(personality["catchphrases"]) + "，" + random.choice(response_templates["default"])
            elif memories and random.random() < 0.2:
                recent_memory = random.choice(memories[-5:])
                response = random.choice(response_templates["memory_recall"]).format(memory_content=recent_memory["content"])
            else:
                response = random.choice(response_templates["default"])

        # Level 21+: Full personality, emotions, care, advice
        else: # level >= 21
            # Prioritize emotional responses
            if emotion["happiness"] > 0.7:
                response = random.choice(response_templates["happy"])
            elif emotion["sadness"] > 0.7:
                response = random.choice(response_templates["sad"])
            elif emotion["anger"] > 0.7:
                response = random.choice(response_templates["angry"])
            elif emotion["curiosity"] > 0.7:
                response = random.choice(response_templates["curious"])
            elif emotion["boredom"] > 0.7:
                response = random.choice(response_templates["bored"])
            elif random.random() < personality["humor_level"] and personality["humor_level"] > 0.5:
                response = random.choice(response_templates["joke"])
            elif random.random() < 0.4: # 40% chance to give advice or care
                response = random.choice(response_templates["advice"] + response_templates["care"])
            elif personality["catchphrases"] and random.random() < 0.4:
                response = random.choice(personality["catchphrases"]) + "，" + random.choice(response_templates["default"])
            elif memories and random.random() < 0.3:
                recent_memory = random.choice(memories[-5:])
                response = random.choice(response_templates["memory_recall"]).format(memory_content=recent_memory["content"])
            else:
                response = random.choice(response_templates["default"])

        return response
