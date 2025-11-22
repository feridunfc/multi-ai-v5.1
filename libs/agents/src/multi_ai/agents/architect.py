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
            "dependencies": ["tkinter", "math"],
            "artifacts": [
                {
                    "path": "main.py",  # ⭐ KRİTİK: MUTLAKA path OLMALI!
                    "purpose": "Ana uygulama mantığı",
                    "instructions": "Detaylı talimatlar..."
                }
            ]
        }

        KRİTİK KURALLAR:
        1. 'artifacts' listesindeki HER öğenin MUTLAKA 'path' field'ı olmalı
        2. 'path' boş string veya null OLMAMALI
        3. Dosya yolları geçerli ve mantıklı olsun
        4. 'dependencies' listesine sadece gerçekten gerekenleri ekle
        """

        context = f"Task: {task}\nResearch: {json.dumps(research_data)}"
        logger.info(f"🏗️ Mimari plan hazırlanıyor...")

        raw_response = await self._ask_llm(system_prompt, context, json_mode=True)

        try:
            manifest = json.loads(raw_response)

            # ⭐ GÜVENLİK KONTROLÜ: Path'leri kontrol et
            artifacts = manifest.get('artifacts', [])
            for artifact in artifacts:
                if not artifact.get('path') or artifact['path'].strip() == '':
                    artifact['path'] = 'main.py'  # Fallback
                    logger.warning("⚠️ Boş path bulundu, fallback kullanılıyor")

            # Eğer artifacts yoksa, default ekle
            if not artifacts:
                manifest['artifacts'] = [{
                    'path': 'main.py',
                    'purpose': 'Main application',
                    'instructions': task
                }]
                logger.warning("⚠️ Hiç artifact yok, default eklendi")

            return manifest

        except json.JSONDecodeError:
            logger.error("Architect JSON üretemedi, Fallback kullanılıyor.")
            return {
                "project_name": "fallback_project",
                "artifacts": [{
                    "path": "main.py",  # ⭐ FALLBACK'te bile path var
                    "purpose": "Single file script",
                    "instructions": task
                }]
            }