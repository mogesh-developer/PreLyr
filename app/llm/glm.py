import os

from dotenv import load_dotenv
from zai import ZaiClient

from app.llm.base import LLMProvider

load_dotenv()


class GLMProvider(LLMProvider):
    def __init__(self, model: str = "glm-4.5-flash"):
        api_key = os.getenv("GLM_API_KEY")

        if not api_key:
            raise ValueError(
                "GLM_API_KEY is not configured."
            )

        self.client = ZaiClient(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            thinking={
                "type": "disabled",
            },
            temperature=0.2,
            max_tokens=1024,
        )

        return response.choices[0].message.content