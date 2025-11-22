import logging
import json
from typing import Dict, Any, List
from .base import BaseAgent

logger = logging.getLogger(__name__)


class EnhancedPromptAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Prompt Engineer", model="qwen2.5:7b")

    async def optimize_prompt(self, original_task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Kullanıcı prompt'unu optimize eder ve diğer ajanlar için hazırlar.
        """
        system_prompt = """
        SEN UZMAN BİR PROMPT MÜHENDİSİSİN (PROMPT ENGINEER).
        Görevin: Kullanıcının girdiği ham talimatı analiz edip, yazılım geliştirme süreci için OPTİMİZE EDİLMİŞ bir talimata dönüştürmektir.

        KRİTİK KURALLAR:
        1. BELİRSİZLİKLERİ GİDER: Eksik detayları mantıklı varsayımlarla tamamla
        2. TEKNİK DETAY EKLE: Hangi kütüphaneler, hangi fonksiyonlar, hangi yapılar
        3. HATA ÖNLEME: Olası hataları önceden tahmin et ve talimata yansıt
        4. ÖLÇÜLEBİLİR YAP: Test edilebilir, net başarı kriterleri belirle
        5. FORMATLA: Okunabilir ve yapılandırılmış çıktı ver

        ÇIKTI FORMATI (JSON):
        {
            "optimized_prompt": "Optimize edilmiş talimat",
            "technical_requirements": ["liste", "of", "requirements"],
            "success_criteria": ["kriter1", "kriter2"],
            "potential_risks": ["risk1", "risk2"],
            "estimated_complexity": "low/medium/high"
        }
        """

        user_context = f"""
        ORJİNAL GÖREV: {original_task}

        EK BAĞLAM: {json.dumps(context or {}, ensure_ascii=False, indent=2)}

        Lütfen bu görevi yazılım geliştirme süreci için optimize et.
        """

        logger.info(f"🎯 Prompt optimize ediliyor: {original_task[:100]}...")

        try:
            raw_response = await self._ask_llm(system_prompt, user_context, json_mode=True)
            result = json.loads(raw_response)

            # Fallback mekanizması
            if not result.get("optimized_prompt"):
                result["optimized_prompt"] = self._fallback_optimization(original_task)

            return result

        except json.JSONDecodeError:
            logger.error("Prompt Agent JSON üretemedi, fallback kullanılıyor.")
            return self._create_fallback_prompt(original_task)

    def _fallback_optimization(self, original_task: str) -> str:
        """Basit prompt optimizasyonu fallback"""
        optimizations = {
            "hesap makinesi": "Python tkinter ile grid layout'ta hesap makinesi. Temel işlemler (+, -, *, /) ve karekök. Matematik hata kontrolleri ekle.",
            "web sitesi": "Flask ile responsive web sitesi. HTML/CSS/JS kullan. Modern tasarım prensipleri uygula.",
            "api": "RESTful API endpoints. CRUD operasyonları, hata yönetimi, validation.",
            "veri analizi": "Pandas ile veri analizi. Temizleme, görselleştirme, raporlama."
        }

        for key, optimized in optimizations.items():
            if key in original_task.lower():
                return optimized

        return f"GELİŞMİŞ {original_task}. Kod tam ve çalışır olmalı. Hata kontrolleri ekle. Temiz ve okunabilir kod yaz."

    def _create_fallback_prompt(self, original_task: str) -> Dict[str, Any]:
        """Fallback prompt oluştur"""
        return {
            "optimized_prompt": f"GELİŞMİŞ SÜRÜM: {original_task}. Tek dosya, tam kod, hata yönetimi, kullanıcı dostu arayüz.",
            "technical_requirements": ["python", "standart kütüphaneler", "hata yönetimi"],
            "success_criteria": ["kod çalışıyor", "testler geçiyor", "kullanıcı dostu"],
            "potential_risks": ["sonsuz döngü", "hata yönetimi eksik", "performans"],
            "estimated_complexity": "medium"
        }