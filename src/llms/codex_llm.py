"""
OpenAI Codex LLM
Usa a API da OpenAI com modelos otimizados para codigo
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM


class CodexLLM(BaseLLM):
    """OpenAI Codex LLM - modelos otimizados para codigo e raciocinio"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API Key nao encontrada! Defina OPENAI_API_KEY ou forneca na inicializacao")

        super().__init__(api_key, model_name)

        self.client = OpenAI(api_key=self.api_key)
        self.default_model = model_name or self.get_default_model()

    def get_default_model(self) -> str:
        return "o3-mini"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            params = {
                "model": self.default_model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }

            # Modelos o3/o4 nao suportam temperature
            if not self.default_model.startswith("o"):
                params["temperature"] = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(**params)

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""

        except Exception as e:
            print(f"Codex API erro: {str(e)}")
            raise e

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "Codex (OpenAI)",
            "model": self.default_model,
            "api_base": "https://api.openai.com"
        }
