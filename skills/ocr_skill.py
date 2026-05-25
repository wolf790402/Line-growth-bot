from skills.base_skill import BaseSkill

class OcrSkill(BaseSkill):
    def __init__(self):
        super().__init__(required_level=10) # Example level requirement

    def can_handle(self, message: str, user_data: dict) -> bool:
        # Placeholder: Check if message indicates OCR request
        return "辨識圖片" in message or "ocr" in message.lower()

    def execute(self, message: str, user_data: dict) -> str:
        if user_data["level"] < self.required_level:
            return f"我還沒學會這個技能，需要等級 {self.required_level} 才能解鎖 OCR 圖片辨識。"
        # Placeholder for OCR logic
        return "這是一個 OCR 圖片辨識的技能。請提供圖片。"
