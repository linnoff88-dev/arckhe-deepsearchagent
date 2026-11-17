"""
Anthropic Claude LLM
Usa a API da Anthropic para modelos Claude
"""

import os
from typing import Optional, Dict, Any
from .base import BaseLLM


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API Key nao encontrada! Defina ANTHROPIC_API_KEY ou forneca na inicializacao")

        super().__init__(api_key, model_name)

        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Instale o SDK da Anthropic: pip install anthropic")

        self.client = Anthropic(api_key=self.api_key)
        self.default_model = model_name or self.get_default_model()

    def get_default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=kwargs.get("max_tokens", 4000),
                temperature=kwargs.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            if response.content:
                content = response.content[0].text
                return self.validate_response(content)
            else:
                return ""

        except Exception as e:
            print(f"Anthropic API erro: {str(e)}")
            raise e

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "Anthropic",
            "model": self.default_model,
            "api_base": "https://api.anthropic.com"
        }
