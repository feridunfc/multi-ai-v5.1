import logging
from typing import Dict, Any, List
from .base import BaseAgent

logger = logging.getLogger(__name__)

class EnhancedResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Researcher", model="llama3.2:3b")

    async def conduct_research(self, query: str) -> Dict[str, Any]:
        system_prompt = """
        SEN KIDEMLİ BİR TEKNİK ARAŞTIRMACISIN (SENIOR TECHNICAL RESEARCHER).
        Görevin: Verilen yazılım görevini analiz etmek ve GÜNCEL, DOĞRU teknik bilgiler sağlamaktır.

        KURALLAR:
        1. ASLA hayali kütüphane veya modül uydurma. Sadece 'requests', 'pandas', 'numpy' gibi standart ve kanıtlanmış kütüphaneleri öner.
        2. Eğer emin değilsen "Bilmiyorum" de, uydurma.
        3. Kodun çalışacağı ortamı (Python 3.10+) göz önünde bulundur.
        4. Çıktın sadece teknik gerçekleri içermeli, laf kalabalığı yapma.
        """

        logger.info(f"🔎 Araştırma yapılıyor: {query}")
        result = await self._ask_llm(system_prompt, query)

        return {
            "query": query,
            "findings": result,
            "source": "Local Knowledge & RAG"
        }