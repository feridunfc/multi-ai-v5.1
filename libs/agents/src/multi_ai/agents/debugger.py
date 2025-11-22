from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class EnhancedDebuggerAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Debugger", model="deepseek-coder:6.7b")

    async def diagnose_error(self, code: str, error_log: str) -> dict:
        system_prompt = """
        SEN UZMAN BİR HATA AYIKLAYICISIN (DEBUGGER).
        Görevin: Verilen bozuk kodu ve hata mesajını analiz edip, HATAYI DÜZELTMEKTİR.
        
        KURALLAR:
        1. Sadece hatayı düzelten kodu ver.
        2. Eğer hata kütüphane eksikliği ise (ModuleNotFoundError), kodu standart kütüphanelerle çalışacak şekilde değiştir veya kullanıcıya uyarı ekle.
        3. Eğer mantık hatası varsa (KeyError, IndexError), kontrol blokları (if/try-except) ekle.
        4. Kodu tamamen yeniden yazma, sadece onarılmış halini ver.
        
        ÇIKTI:
        Sadece düzeltilmiş Python kodu.
        """
        
        prompt = f"BOZUK KOD:\n{code}\n\nHATA MESAJI:\n{error_log}"
        logger.info("🚑 Hata analizi yapılıyor...")
        
        fixed_code = await self._ask_llm(system_prompt, prompt)
        
        # Markdown temizliği
        if "`python" in fixed_code:
            fixed_code = fixed_code.split("`python")[1].split("`")[0]
            
        return {"fixed_code": fixed_code.strip(), "diagnosis": "AI fix applied"}
