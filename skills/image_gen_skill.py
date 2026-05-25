from skills.base_skill import BaseSkill

class ImageGenSkill(BaseSkill):
    def __init__(self):
        super().__init__(required_level=15) # Example level requirement

    def can_handle(self, message: str, user_data: dict) -> bool:
        # Placeholder: Check if message indicates image generation request
        return "生成圖片" in message or "畫圖" in message or "image gen" in message.lower()

    def execute(self, message: str, user_data: dict) -> str:
        if user_data["level"] < self.required_level:
            return f"我還沒學會這個技能，需要等級 {self.required_level} 才能解鎖圖片生成。"
        # Placeholder for image generation logic
        return "這是一個圖片生成的技能。請描述您想生成的圖片。"
