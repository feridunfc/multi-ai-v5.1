import httpx
import logging
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class RobustOllamaClient:
    def __init__(self):
        # Windows ve Docker uyumluluğu için 127.0.0.1 şart
        self.base_url = "http://127.0.0.1:11434"
        self.timeout = 120.0  # Büyük modeller için süreyi uzun tutuyoruz

    async def _pull_model_if_missing(self, model: str):
        """Eğer model yoksa (404 hatası alırsak) indirmeyi dener."""
        logger.info(f"📥 '{model}' modeli bulunamadı, otomatik indiriliyor...")
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                # Pull isteği (Stream kapalı)
                await client.post(f"{self.base_url}/api/pull", json={"name": model, "stream": False})
                logger.info(f"✅ '{model}' başarıyla indirildi!")
            except Exception as e:
                logger.error(f"❌ Model indirme hatası: {e}")

    # HTTP hatalarını da (500, 503 vb.) kapsayacak şekilde retry ayarla
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError))
    )
    async def generate(self, model: str, prompt: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": options or {"temperature": 0.2}
            }

            try:
                # 1. GENERATE Endpoint Dene
                response = await client.post(f"{self.base_url}/api/generate", json=payload)

                # Eğer model yoksa (404), indir ve tekrar dene
                if response.status_code == 404:
                    await self._pull_model_if_missing(model)
                    # Tekrar dene
                    response = await client.post(f"{self.base_url}/api/generate", json=payload)

                response.raise_for_status()
                return response.json()

            except Exception as e:
                logger.warning(f"⚠️ Generate endpoint hatası: {e}. Chat endpoint deneniyor...")

                # 2. CHAT Endpoint Dene (Fallback)
                try:
                    chat_payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": options or {"temperature": 0.2}
                    }
                    response = await client.post(f"{self.base_url}/api/chat", json=chat_payload)

                    # Model yoksa burada da indir
                    if response.status_code == 404:
                        await self._pull_model_if_missing(model)
                        response = await client.post(f"{self.base_url}/api/chat", json=chat_payload)

                    response.raise_for_status()
                    res_json = response.json()

                    # Chat formatını Generate formatına çevir
                    content = res_json.get("message", {}).get("content", "")
                    return {"response": content}

                except Exception as e2:
                    logger.error(f"❌ Tüm Ollama denemeleri başarısız. Hata: {e2}")
                    raise e2