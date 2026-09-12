import json
import os

import requests
from utils.ai_service import AIResponse, BaseAIService


class OllamaAIService(BaseAIService):
    def analyze_work_item(
        self, system_prompt: str, title: str, description: str
    ) -> AIResponse:
        try:
            OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
            prompt = f"{system_prompt}\n\nTicket Title: {title}\nTicket Description: {description}"
            response = requests.post(
                url=OLLAMA_URL,
                json={
                    "model": "llama3.1",
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                    },
                },
                timeout=15,
            )
            response.raise_for_status()
            try:
                data = response.json()
                raw_text = data.get("response", "")
                result = AIResponse(
                    type="Success",
                    message=json.loads(raw_text),
                )
            except json.JSONDecodeError as e:
                result = AIResponse(
                    type="Error",
                    message=f"Invalid JSON response from LLM: {e}",
                )
            required_keys = {"category", "priority", "summary", "recommendedAction"}
            if not isinstance(result.message, dict) or not required_keys.issubset(
                result.message.keys()
            ):
                return AIResponse(
                    type="Error",
                    message=f"LLM response does not match the expected schema for work item {result.message}",
                )
            return result
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            return AIResponse(
                type="Error",
                message=str(e),
            )
