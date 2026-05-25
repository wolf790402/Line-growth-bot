import abc

class BaseSkill(abc.ABC):
    def __init__(self, required_level: int):
        self.required_level = required_level

    @abc.abstractmethod
    def can_handle(self, message: str, user_data: dict) -> bool:
        """Determines if this skill can handle the given message."""
        pass

    @abc.abstractmethod
    def execute(self, message: str, user_data: dict) -> str:
        """Executes the skill and returns a response."""
        pass
