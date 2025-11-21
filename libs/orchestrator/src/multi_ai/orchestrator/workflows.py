from datetime import timedelta
from temporalio import workflow
from .activities import AgentActivities, AgentInput


@workflow.defn
class SupervisorWorkflow:
    def __init__(self):
        self.current_context = None  # Manuel müdahale ile değiştirilen veri
        self.next_step = None  # Ajan atlama hedefi

    # --- SİNYAL METODLARI (Dashboard Etkileşimi İçin) ---
    @workflow.signal
    def override_context(self, data: dict):
        """Kullanıcının arayüzden gönderdiği düzeltilmiş veriyi kabul eder."""
        new_content = data.get("new_content")
        workflow.logger.info(f"⚠️ KULLANICI MÜDAHALESİ: İçerik manuel olarak değiştirildi.")
        self.current_context = new_content

    @workflow.signal
    def jump_to_phase(self, data: dict):
        """Süreci belirli bir ajana atlatır."""
        target = data.get("target_phase")
        instruction = data.get("instruction")
        workflow.logger.info(f"⏭️ FAZ ATLAMA: {target} hedefine gidiliyor. Not: {instruction}")
        self.next_step = target
        # Basitlik için şimdilik sadece logluyoruz, gelişmiş versiyonda state machine güncellenir.

    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Sprint 7: Self-Healing Workflow Started')

        # Veri temizliği (Event Payload veya Dictionary gelme durumu)
        if isinstance(event_payload, dict):
            task_id = 'task_auto'
            title = event_payload.get('task_description') or event_payload.get('pull_request', {}).get('title', 'Task')
        else:
            task_id = 'task_auto'
            title = str(event_payload)

        # =====================================================================
        # 1. PLANLAMA (Researcher -> Architect)
        # =====================================================================
        workflow.logger.info("⏳ AŞAMA 1: Araştırma ve Planlama Başlıyor...")

        # Timeout: 5 Dakika (Araştırma uzun sürebilir)
        res = await workflow.execute_activity(
            AgentActivities.research_task,
            AgentInput(task_id, title, event_payload),
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Timeout: 5 Dakika (Mimar planı uzun sürebilir)
        arch = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(task_id, title, {'research_data': res.data}),
            start_to_close_timeout=timedelta(minutes=5)
        )

        # =====================================================================
        # 2. KODLAMA
        # =====================================================================
        workflow.logger.info("⏳ AŞAMA 2: Kodlama Başlıyor (Lütfen Bekleyin)...")

        # Eğer kullanıcı arayüzden planı değiştirdiyse onu kullan
        manifest_data = self.current_context if self.current_context else arch.data

        # Timeout: 20 DAKİKA! (Local LLM yavaş yazabilir, kesilmemesi için artırdık)
        code_out = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(task_id, 'Implement', {'manifest': manifest_data}),
            start_to_close_timeout=timedelta(minutes=20)
        )
        current_file = code_out.file_path

        # =====================================================================
        # 3. SELF-HEALING LOOP (Test -> Debug -> Fix)
        # =====================================================================
        max_retries = 3
        is_stable = False

        for attempt in range(max_retries):
            workflow.logger.info(f'🔄 Testing Cycle: {attempt + 1}/{max_retries}')

            # Test Et (Timeout: 2 Dakika)
            test_res = await workflow.execute_activity(
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

                # Debug Et ve Duzelt (Timeout: 15 Dakika - Düzeltme uzun sürer)
                workflow.logger.info("🚑 Debugger devreye giriyor...")
                fix_out = await workflow.execute_activity(
                    AgentActivities.debugger_fix,
                    AgentInput(task_id, current_file, {'error_log': test_res.result}),
                    start_to_close_timeout=timedelta(minutes=15)
                )
                # Dosya yolunu guncelle
                current_file = fix_out.file_path

        if not is_stable:
            return {'status': 'FAILED', 'reason': 'Max retries exceeded. Code is still broken.'}

        # =====================================================================
        # 4. GÜVENLİK (Compliance)
        # =====================================================================
        workflow.logger.info("🛡️ Güvenlik Taraması...")
        comp = await workflow.execute_activity(
            AgentActivities.compliance_check,
            AgentInput(task_id, current_file, {}),
            start_to_close_timeout=timedelta(minutes=2)
        )

        if comp.status == 'failed':
            return {'status': 'BLOCKED', 'reason': comp.result}

        # =====================================================================
        # 5. YAYIN (Publisher)
        # =====================================================================
        workflow.logger.info("📦 Yayınlanıyor...")
        pub = await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(task_id, current_file, {}),
            start_to_close_timeout=timedelta(minutes=2)
        )

        workflow.logger.info("✅ SÜREÇ BAŞARIYLA TAMAMLANDI")
        return {'status': 'SUCCESS', 'file': current_file}