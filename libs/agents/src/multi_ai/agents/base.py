import logging
import json
import re
from typing import Any, Dict, Optional, List
from multi_ai.utils.robust_ollama_client import RobustOllamaClient

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, role: str, model: str = "deepseek-coder:6.7b"):
        self.role = role
        self.model = model
        self.llm = RobustOllamaClient()

    async def _ask_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUSER TASK:\n{user_prompt}"
            response_json = await self.llm.generate(
                model=self.model, 
                prompt=full_prompt,
                options={"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096}
            )
            
            content = response_json.get("response", "").strip()
            
            # 1. KRİTİK TEMİZLİK: Kontrol tokenlarını temizle
            content = self._clean_control_tokens(content) 
            
            if json_mode:
                content = self._extract_json(content)
            
            return content
        except Exception as e:
            logger.error(f"LLM Error in {self.role}: {e}")
            raise

    def _clean_control_tokens(self, text: str) -> str:
        """LLM'den gelen zararlı kontrol tokenlarını ve <|TOKEN|> yapılarını temizler."""
        if not text:
            return ""
        
        # Llama'nın kullandığı tüm özel tokenları temizle
        text = re.sub(r'<\|[^>]*?\|?>', '', text) 
        text = text.replace("｜begin of sentence｜", "") 
        
        return text.strip()
    
    def _extract_json(self, text: str) -> str:
        # JSON çıkarma mantığı (gerekli)
        try:
            if "```" in text:
                match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
                if match:
                    text = match.group(1).strip()
            return text
        except:
            return text
