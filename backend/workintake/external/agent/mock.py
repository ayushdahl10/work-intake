import time

from utils.ai_service import AIResponse, BaseAIService


class MockAIService(BaseAIService):
    def analyze_work_item(
        self, system_prompt: str, title: str, description: str
    ) -> AIResponse:

        time.sleep(2)

        if "fail" in title.lower():
            return AIResponse(
                type="Error", message="Mock AI Service failed to analyze work item"
            )

        return AIResponse(
            type="Success",
            message={
                "category": "Bug Report",
                "priority": "HIGH",
                "summary": "Mock AI Service analyzed work item",
                "recommendedAction": "Mock AI Service recommended next action",
            },
        )
