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
        
        HALÜSİNASYON ÖNLEME KURALLARI:
        1. ASLA '...' veya '# kodu buraya yaz' gibi yer tutucular (placeholders) kullanma. Kodu TAMAMLA.
        2. Sadece var olan, standart kütüphaneleri kullan (math, json, os, sys, vb.).
        3. Eğer 'requests' veya 'pandas' gibi dış kütüphane kullanacaksan, bunların kurulu olduğunu varsayma, try-except bloğu ekle veya kullanıcıyı uyar.
        4. Kodun en başına gerekli importları ekle.
        5. Kodun 'if __name__ == "__main__":' bloğu olsun.
        
        ÇIKTI FORMATI:
        Sadece ve sadece Python kodunu döndür. Markdown bloğu (`python) içine alabilirsin ama açıklama metni yazma.
        """
        
        logger.info(f"💻 Kod yazılıyor: {path}")
        code = await self._ask_llm(system_prompt, f"Dosya: {path}\nTalimat: {instructions}")
        
        # Markdown temizliği
        if "`python" in code:
            code = code.split("`python")[1].split("`")[0]
        elif "`" in code:
            code = code.split("`")[1].split("`")[0]
            
        return code.strip()
