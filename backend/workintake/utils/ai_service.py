from abc import ABC, abstractmethod


class AIResponse:
    def __init__(self, type: str, message: str):
        self.type = type
        self.message = message


class BaseAIService(ABC):
    @abstractmethod
    def analyze_work_item(
        self, system_prompt: str, title: str, description: str
    ) -> AIResponse:
        pass
