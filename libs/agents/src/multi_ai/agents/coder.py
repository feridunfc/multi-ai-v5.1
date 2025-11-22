from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class EnhancedCoderAgent(BaseAgent):
    def __init__(self):
        # Kodlama için en iyi model
        super().__init__(role="Coder", model="deepseek-coder:6.7b")

    async def implement_artifact(self, artifact: dict, task_id: str) -> str:
        path = artifact.get('path')
        instructions = artifact.get('instructions')

        system_prompt = f"""
        SEN GOOGLE SEVİYESİNDE BİR KIDEMLİ YAZILIM MÜHENDİSİSİN (SENIOR SOFTWARE ENGINEER).
        Görevin: '{path}' dosyasını, verilen talimatlara göre SIFIRDAN yazmaktır.

        📋 KRİTİK KURALLAR:
        1. SADECE talimatlarda istenen kütüphaneleri kullan (tkinter, math)
        2. ASLA gereksiz kütüphane ekleme (pandas, numpy, requests, flask, django YOK)
        3. Kod TAM ve ÇALIŞIR olmalı - placeholder (# ...) YOK
        4. Hata kontrolleri ekle (sıfıra bölme, negatif karekök)
        5. Tkinter için grid layout kullan
        6. Sınıf (Class) yapısı kullan

        🚫 YASAKLI KÜTÜPHANELER:
        - pandas, numpy, requests, flask, django, tensorflow, torch

        ✅ İZİNLİ KÜTÜPHANELER:
        - tkinter, math, os, sys

        ÇIKTI FORMATI:
        Sadece ve sadece Python kodunu döndür. Açıklama yazma.
        """
        
        logger.info(f"💻 Kod yazılıyor: {path}")
        code = await self._ask_llm(system_prompt, f"Dosya: {path}\nTalimat: {instructions}")
        
        # Markdown temizliği
        if "`python" in code:
            code = code.split("`python")[1].split("`")[0]
        elif "`" in code:
            code = code.split("`")[1].split("`")[0]
            
        return code.strip()
