import logging
import json
from typing import Dict, Any, List
from .base import BaseAgent

logger = logging.getLogger(__name__)

class EnhancedArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Architect", model="qwen2.5:7b")

    async def create_manifest(self, research_data: dict, task: str) -> Dict[str, Any]:
        system_prompt = """
        SEN BAŞ YAZILIM MİMARISIN (CHIEF SOFTWARE ARCHITECT).
        Görevin: Verilen görevi, hatasız çalışacak bir dosya yapısına ve uygulama planına dönüştürmektir.

        ÇIKTI FORMATI (KESİNLİKLE JSON):
        {
            "project_name": "proje_adi",
            "description": "Proje açıklaması",
            "dependencies": ["flask", "requests"],
            "artifacts": [
                {
                    "path": "main.py",
                    "purpose": "Ana uygulama mantığı",
                    "instructions": "Detaylı talimatlar..."
                }
            ]
        }

        KURALLAR:
        1. Sadece geçerli JSON döndür. Başka hiçbir metin yazma.
        2. Dosya yolları mantıklı ve düzenli olsun.
        3. 'dependencies' listesine sadece gerçekten gerekenleri ekle.
        """

        context = f"Task: {task}\nResearch: {json.dumps(research_data)}"
        logger.info(f"🏗️ Mimari plan hazırlanıyor...")

        raw_response = await self._ask_llm(system_prompt, context, json_mode=True)

        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            logger.error("Architect JSON üretemedi, Fallback kullanılıyor.")
            return {
                "project_name": "fallback_project",
                "artifacts": [{"path": "main.py", "purpose": "Single file script", "instructions": task}]
            }