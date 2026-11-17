"""
Ollama LLM - Modelos locais via Ollama
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    """Ollama LLM - executa modelos localmente"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None,
                 base_url: Optional[str] = None):
        # Ollama nao precisa de api_key real, mas a interface exige
        super().__init__(api_key or "ollama", model_name)

        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        # Ollama expoe API compativel com OpenAI
        self.client = OpenAI(
            api_key="ollama",
            base_url=self.base_url
        )

        self.default_model = model_name or self.get_default_model()

    def get_default_model(self) -> str:
        return "llama3.1"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            params = {
                "model": self.default_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }

            response = self.client.chat.completions.create(**params)

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""

        except Exception as e:
            print(f"Ollama API erro: {str(e)}")
            raise e

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "Ollama",
            "model": self.default_model,
            "api_base": self.base_url
        }
