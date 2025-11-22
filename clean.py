import os
import re

import logging
import json
import re
from typing import Any, Dict, Optional, List
from multi_ai.utils.robust_ollama_client import RobustOllamaClient

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, role: str, model: str = "llama3.2:1b"):
        self.role = role
        self.model = model
        self.llm = RobustOllamaClient()

    async def _ask_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        # Kodun içindeki bu method, LLM'den gelen çıktıyı alır ve temizler.
        try:
            full_prompt = f"{system_prompt}\\n\\nUSER TASK:\\n{user_prompt}"

            # Ollama'dan cevabı al
            response_json = await self.llm.generate(
                model=self.model,
                prompt=full_prompt,
                options={"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096}
            )

            # 1. Ham metni al
            content = response_json.get("response", "").strip()

            # 2. KRİTİK TEMİZLİK: Kontrol tokenlarını temizle
            content = self._clean_control_tokens(content)

            if json_mode:
                content = self._extract_json(content)

            return content
        except Exception as e:
            logger.error(f"LLM Error in {self.role}: {e}")
            raise

    def _clean_control_tokens(self, text: str) -> str:
        # LLAMA ve DeepSeek'in kullandığı zararlı tokenları temizle
        if not text:
            return ""

        text = text.replace("<|begin_of_text|>", "")
        text = text.replace("<|EOT|>", "")
        text = text = re.sub(r'<\|[^>]*?\|>', '', text) # Diğer tüm özel tokenları temizle
        return text.strip()

    def _extract_json(self, text: str) -> str:
        # ... (Diğer JSON çıkarma mantığı) ...
        try:
            if "```" in text:
                match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
                if match:
                    text = match.group(1).strip()
            return text
        except:
            return text


