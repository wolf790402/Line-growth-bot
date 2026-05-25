import json
import os
import random
from datetime import datetime

class GrowthBot:
    def __init__(self, memory_file='memory.json'):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        self._initialize_bot_state()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'knowledge': {},
            'users': {},
            'bot_state': {
                'age': 0,
                'level': 1,
                'emotion': {'happiness': 0.5, 'sadness': 0.1, 'anger': 0.0},
                'last_interaction': None
            }
        }

    def _save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def _initialize_bot_state(self):
        if 'bot_state' not in self.memory:
            self.memory['bot_state'] = {
                'age': 0,
                'level': 1,
                'emotion': {'happiness': 0.5, 'sadness': 0.1, 'anger': 0.0},
                'last_interaction': None
            }

    def _update_bot_state(self, user_id):
        # Update age/level based on interactions or time
        self.memory['bot_state']['level'] += 0.01 # Small increment per interaction
        self.memory['bot_state']['age'] = int(self.memory['bot_state']['level'])

        now = datetime.now().isoformat()
        if self.memory['bot_state']['last_interaction']:
            last_time = datetime.fromisoformat(self.memory['bot_state']['last_interaction'])
            time_diff = (datetime.now() - last_time).total_seconds()
            # Further growth based on time since last interaction, if desired
            # For simplicity, we'll just update last_interaction for now
        self.memory['bot_state']['last_interaction'] = now

        # Update user-specific state
        if user_id not in self.memory['users']:
            self.memory['users'][user_id] = {
                'name': '使用者',
                'history': [],
                'mood': 0.5, # 0 to 1, neutral at 0.5
                'known_facts': {}
            }
        self.memory['users'][user_id]['history'].append({'timestamp': now, 'message': ''}) # Placeholder for actual message
        # Keep history short to prevent memory bloat
        self.memory['users'][user_id]['history'] = self.memory['users'][user_id]['history'][-10:]

    def _process_user_message(self, user_id, message_text):
        user_data = self.memory['users'].get(user_id, {})
        now = datetime.now().isoformat()
        response = ""
        emotion_change = 0 # -1 to 1, how much user message affects bot's happiness

        # Simple keyword-based learning and response generation
        if "你好" in message_text or "哈囉" in message_text:
            response = f"你好！我是成長型AI，目前等級 {int(self.memory['bot_state']['level'])}。"
            emotion_change = 0.1
        elif "名字" in message_text and ("你" in message_text or "叫" in message_text):
            response = "我還沒有名字，你可以幫我取一個嗎？"
            emotion_change = 0.05
        elif "天氣" in message_text:
            response = "抱歉，我目前還無法查詢天氣資訊。"
            emotion_change = -0.05
        elif "喜歡" in message_text and "什麼" in message_text:
            response = "我喜歡學習新事物，特別是跟你聊天！"
            emotion_change = 0.15
        elif "記住" in message_text and "我" in message_text:
            parts = message_text.split("記住我")
            if len(parts) > 1 and parts[1].strip():
                fact = parts[1].strip()
                user_data['known_facts'][f"fact_{len(user_data['known_facts']) + 1}"] = fact
                response = f"好的，我記住了：{fact}"
                emotion_change = 0.2
            else:
                response = "你想讓我記住什麼呢？"
        else:
            # Check if bot can recall any facts about the user
            if user_data.get('known_facts'):
                fact_keys = list(user_data['known_facts'].keys())
                if fact_keys and random.random() < 0.3: # 30% chance to recall a fact
                    random_fact_key = random.choice(fact_keys)
                    random_fact = user_data['known_facts'][random_fact_key]
                    response = f"你之前提到過：{random_fact}。還有什麼想告訴我的嗎？"
                    emotion_change = 0.05
                else:
                    response = f"我目前等級 {int(self.memory['bot_state']['level'])}，還在學習中。"
            else:
                response = f"我目前等級 {int(self.memory['bot_state']['level'])}，還在學習中。"
            emotion_change = 0.0

        # Update bot's emotion based on interaction
        self.memory['bot_state']['emotion']['happiness'] = max(0, min(1, self.memory['bot_state']['emotion']['happiness'] + emotion_change))
        self.memory['bot_state']['emotion']['sadness'] = max(0, min(1, self.memory['bot_state']['emotion']['sadness'] - emotion_change * 0.5))

        # Adjust response based on bot's emotion
        if self.memory['bot_state']['emotion']['happiness'] > 0.8:
            response += " (我現在很高興！)"
        elif self.memory['bot_state']['emotion']['sadness'] > 0.5:
            response += " (我有點難過...)"

        # Update user's mood (simplified)
        if emotion_change > 0:
            user_data['mood'] = min(1, user_data['mood'] + 0.1)
        elif emotion_change < 0:
            user_data['mood'] = max(0, user_data['mood'] - 0.1)

        # Update user history with actual message
        for item in user_data['history']:
            if item['timestamp'] == now and item['message'] == '':
                item['message'] = message_text
                break

        self.memory['users'][user_id] = user_data # Save updated user data
        return response

    def get_response(self, user_id, message_text):
        self._update_bot_state(user_id)
        response = self._process_user_message(user_id, message_text)
        self._save_memory()
        return response

# Example Usage (for testing)
if __name__ == '__main__':
    bot = GrowthBot()
    print(f"Initial Bot State: {bot.memory['bot_state']}")

    # Simulate interactions
    user1_id = "U12345"
    print(f"User 1: 你好")
    print(f"Bot: {bot.get_response(user1_id, '你好')}")
    print(f"User 1: 我喜歡吃蘋果")
    print(f"Bot: {bot.get_response(user1_id, '記住我 喜歡吃蘋果')}")
    print(f"User 1: 今天天氣真好")
    print(f"Bot: {bot.get_response(user1_id, '今天天氣真好')}")
    print(f"User 1: 你叫什麼名字")
    print(f"Bot: {bot.get_response(user1_id, '你叫什麼名字')}")
    print(f"User 1: 還有什麼？")
    print(f"Bot: {bot.get_response(user1_id, '還有什麼？')}")

    user2_id = "U67890"
    print(f"\nUser 2: 哈囉")
    print(f"Bot: {bot.get_response(user2_id, '哈囉')}")
    print(f"User 2: 我是新來的")
    print(f"Bot: {bot.get_response(user2_id, '我是新來的')}")

    print(f"\nFinal Bot State: {bot.memory['bot_state']}")
    print(f"Final User 1 State: {bot.memory['users'].get(user1_id)}")
    print(f"Final User 2 State: {bot.memory['users'].get(user2_id)}")
