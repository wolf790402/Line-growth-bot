from skills.base_skill import BaseSkill

class CodeSkill(BaseSkill):
    def __init__(self):
        super().__init__(required_level=25) # Example level requirement

    def can_handle(self, message: str, user_data: dict) -> bool:
        # Placeholder: Check if message indicates code related request
        return "寫程式" in message or "debug" in message.lower() or "code" in message.lower()

    def execute(self, message: str, user_data: dict) -> str:
        if user_data["level"] < self.required_level:
            return f"我還沒學會這個技能，需要等級 {self.required_level} 才能解鎖寫程式。"
        # Placeholder for code generation/debugging logic
        return "這是一個寫程式的技能。請告訴我您需要什麼程式碼或問題。"
