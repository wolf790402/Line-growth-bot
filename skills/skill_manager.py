import os
import importlib
from skills.base_skill import BaseSkill

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.skills = self._load_skills()

    def _load_skills(self):
        loaded_skills = []
        # Ensure skills directory exists
        if not os.path.exists(self.skills_dir):
            print(f"Warning: Skills directory '{self.skills_dir}' not found.")
            return loaded_skills

        for filename in os.listdir(self.skills_dir):
            if filename.endswith("_skill.py") and filename != "base_skill.py":
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Dynamically import the module
                    module = importlib.import_module(f"skills.{module_name}")
                    # Find the skill class within the module (convention: class name is CamelCase of module name)
                    class_name = "".join([word.capitalize() for word in module_name.split('_')])
                    skill_class = getattr(module, class_name)

                    # Instantiate the skill and add to the list
                    if issubclass(skill_class, BaseSkill) and skill_class is not BaseSkill:
                        loaded_skills.append(skill_class())
                        print(f"Loaded skill: {class_name}")
                except Exception as e:
                    print(f"Error loading skill {module_name}: {e}")
        return loaded_skills

    def get_skill_response(self, message: str, user_data: dict) -> str | None:
        for skill in self.skills:
            if skill.can_handle(message, user_data):
                return skill.execute(message, user_data)
        return None
