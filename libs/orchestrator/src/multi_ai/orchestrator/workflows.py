from datetime import timedelta
from temporalio import workflow
import json
from .activities import AgentActivities, AgentInput, AgentOutput
from temporalio import workflow

# Temporal, bu sınıfı hafızasında tuttuğu için bu field'lar ile sinyalleri yakalayabiliriz.
@workflow.defn
class SupervisorWorkflow:
    def __init__(self):
        # Human-in-the-Loop için state'leri tanımla
        self.current_context = None
        self.retry_count = 0
        self.model_map = {}

    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Sprint 7: Self-Healing Workflow Started')

        # Payload'dan veri ve model haritasını güvenle al
        task_description = event_payload.get('task_description', 'Default Task')
        self.model_map = event_payload.get('metadata', {}).get('role_map', {})

        # Output ve AgentInput'lar için task_id sabit kalacak
        task_id = 'task_auto'
        current_file = ''  # Kodlandıktan sonra dosya yolunu tutacak

        # ---------------------------------------------------------------------
        # AŞAMA 1: PLANLAMA (Researcher -> Architect)
        # ---------------------------------------------------------------------
        workflow.logger.info("⏳ AŞAMA 1: Araştırma ve Planlama Başlıyor...")

        # Researcher: Sadece metin talimatını gönderiyor.
        res = await workflow.execute_activity(
            AgentActivities.research_task,
            AgentInput(task_id, task_description, self.model_map),
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Architect: Manifestoyu oluşturuyor.
        arch = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(task_id, task_description, {'research_data': res.data}),
            start_to_close_timeout=timedelta(minutes=5)
        )

        # ---------------------------------------------------------------------
        # AŞAMA 2: KODLAMA
        # ---------------------------------------------------------------------
        workflow.logger.info("⏳ AŞAMA 2: Kodlama Başlıyor...")

        # Coder: Kod yazdırıyor, dosya yolunu alıyoruz
        code_out = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(task_id, 'Implement Code', {'manifest': arch.data}),
            start_to_close_timeout=timedelta(minutes=20)
        )
        current_file = code_out.file_path  # Dosya yolu artık burada

        # ---------------------------------------------------------------------
        # AŞAMA 3: SELF-HEALING LOOP (TEST -> DEBUG -> FIX)
        # ---------------------------------------------------------------------
        max_retries = 3
        is_stable = False

        for attempt in range(max_retries):
            workflow.logger.info(f'🔄 Testing Cycle: {attempt + 1}/{max_retries}')

            # Test Et: KRİTİK DÜZELTME: Dosya yolunu instruction olarak gönderiyoruz
            test_res: AgentOutput = await workflow.execute_activity(
                AgentActivities.tester_run,
                AgentInput(task_id, current_file, {}),
                start_to_close_timeout=timedelta(minutes=2)
            )

            if test_res.status == 'success':
                workflow.logger.info('✅ Tests Passed!')
                is_stable = True
                break
            else:
                workflow.logger.error(f'❌ Tests Failed: {test_res.result}')

                # Debug Et ve Duzelt (Dosya yolu ve hata logunu gönder)
                workflow.logger.info("🚑 Debugger devreye giriyor...")
                fix_out = await workflow.execute_activity(
                    AgentActivities.debugger_fix,
                    AgentInput(task_id, current_file, {'error_log': test_res.result}),
                    start_to_close_timeout=timedelta(minutes=15)
                )
                # Dosya yolu aynı kalır, içerik güncellenir.

        if not is_stable:
            return {'status': 'FAILED', 'reason': 'Max retries exceeded. Code is still broken.'}

        # ---------------------------------------------------------------------
        # AŞAMA 4 & 5: GÜVENLİK VE YAYIN
        # ---------------------------------------------------------------------
        workflow.logger.info("🛡️ Güvenlik ve Yayın Aşaması...")

        await workflow.execute_activity(
            AgentActivities.compliance_check,
            AgentInput(task_id, current_file, {}),
            start_to_close_timeout=timedelta(minutes=2)
        )

        await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(task_id, current_file, {}),
            start_to_close_timeout=timedelta(minutes=2)
        )

        workflow.logger.info("✅ SÜREÇ BAŞARIYLA TAMAMLANDI")
        return {'status': 'SUCCESS', 'file': current_file}

    # Sinyal Metotları (Human-in-the-Loop için)
    @workflow.signal
    def override_context(self, data: dict):
        """Kodu manuel olarak düzeltir ve Coder'ı atlar."""
        self.current_context = data.get("new_content")
        workflow.logger.info("⚠️ KOD MANUEL OLARAK DÜZELTİLDİ. YENİ KOD KULLANILACAK.")

    @workflow.signal
    def retry_phase(self, data: dict):
        """Mevcut fazı yeniden dener (örneğin Test fazı)."""
        # Basitlik için sadece logluyoruz, gelişmiş versiyonda fazı resetleriz.
        workflow.logger.info("🔄 KULLANICI İSTEĞİ ÜZERİNE TEST FAZI YENİDEN TETİKLENİYOR.")