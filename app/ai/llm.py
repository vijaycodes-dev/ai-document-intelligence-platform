import os

from ollama import Client


class LLMService:

    MODEL_NAME = "gemma3:4b"

    OLLAMA_HOST = os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434",
    )

    client = Client(host=OLLAMA_HOST)

    @classmethod
    def generate(cls, prompt: str) -> str:
        response = cls.client.chat(
            model=cls.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]


# Backward compatibility for existing services
def generate_response(prompt: str) -> str:
    return LLMService.generate(prompt)