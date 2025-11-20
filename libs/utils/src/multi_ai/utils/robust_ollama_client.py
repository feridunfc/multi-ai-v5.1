import logging
import httpx
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class RobustOllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = 120.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout))
    )
    async def generate(self, model: str, prompt: str, options: Optional[Dict] = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": options or {"temperature": 0.7}
                }
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                # Mocking a response object for compatibility
                return type("OllamaResponse", (), {"content": data.get("response", "")})
            except Exception as e:
                logger.warning(f"Ollama Connection Failed: {e}")
                raise e
