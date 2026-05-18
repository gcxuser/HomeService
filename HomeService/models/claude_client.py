from openai import OpenAI
from typing import List, Dict
from HomeService.config import settings

class ClaudeClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.claude_api_key,
            base_url=settings.claude_base_url,
        )
        self.model_name = settings.claude_model_name

    def chat(self, messages: List[Dict], stream: bool = False) -> str:
        if not settings.claude_api_key:
            raise ValueError("CLAUDE_API_KEY is not configured")

        if stream:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
            )
            result = []
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    result.append(chunk.choices[0].delta.content)
            return "".join(result)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content
