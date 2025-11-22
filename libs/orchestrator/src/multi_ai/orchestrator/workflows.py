from datetime import timedelta
from temporalio import workflow
import json
import os
from .activities import AgentActivities, AgentInput, AgentOutput


@workflow.defn
class SupervisorWorkflow:
    def __init__(self):
        self.current_context = None
        self.retry_count = 0
        self.model_map = {}
        self.generated_code = ""
        self.optimized_prompt = ""

    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Sprint 7: Self-Healing Workflow Started')

        task_description = event_payload.get('task_description', 'Default Task')
        self.model_map = event_payload.get('metadata', {}).get('role_map', {})
        task_id = 'task_auto'
        current_file = ''

        # ---------------------------------------------------------------------
        # AŞAMA 0: PROMPT OPTIMIZATION
        # ---------------------------------------------------------------------
        workflow.logger.info("🎯 AŞAMA 0: Prompt Optimizasyonu Başlıyor...")

        prompt_result = await workflow.execute_activity(
            AgentActivities.prompt_optimize,
            AgentInput(task_id, task_description, self.model_map),
            start_to_close_timeout=timedelta(minutes=3)
        )

        if prompt_result.status == 'success':
            optimized_data = prompt_result.data
            self.optimized_prompt = optimized_data.get('optimized_prompt', task_description)
            workflow.logger.info(f"✅ Prompt optimize edildi: {self.optimized_prompt[:100]}...")
        else:
            self.optimized_prompt = task_description
            workflow.logger.warning("⚠️ Prompt optimizasyonu başarısız, orjinal prompt kullanılıyor")

        # ---------------------------------------------------------------------
        # AŞAMA 1: PLANLAMA (Researcher -> Architect)
        # ---------------------------------------------------------------------
        workflow.logger.info("⏳ AŞAMA 1: Araştırma ve Planlama Başlıyor...")

        # Optimize edilmiş prompt'u kullan
        res = await workflow.execute_activity(
            AgentActivities.research_task,
            AgentInput(task_id, self.optimized_prompt, self.model_map),
            start_to_close_timeout=timedelta(minutes=5)
        )

        arch = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(
                task_id,
                self.optimized_prompt,
                {
                    'research_data': res.data,
                    'prompt_analysis': prompt_result.data if prompt_result.status == 'success' else {}
                }
            ),
            start_to_close_timeout=timedelta(minutes=5)
        )

        # ---------------------------------------------------------------------
        # AŞAMA 2: KODLAMA
        # ---------------------------------------------------------------------
        workflow.logger.info("⏳ AŞAMA 2: Kodlama Başlıyor...")

        # Workflow'da coder'dan sonra:
        code_out = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(
                task_id,
                self.optimized_prompt,
                {
                    'manifest': arch.data,
                    'prompt_analysis': prompt_result.data if prompt_result.status == 'success' else {}
                }
            ),
            start_to_close_timeout=timedelta(minutes=20)
        )

        # ⭐ KRİTİK: Coder çıktısını GÜVENLİ şekilde al
        current_file = code_out.file_path if code_out.file_path else 'main.py'
        self.generated_code = code_out.data.get('code_content', '') if code_out.data else ''

        # Eğer coder hata verdi ama fallback path varsa
        if code_out.status == 'error' and not current_file:
            current_file = 'main.py'
            workflow.logger.warning("⚠️ Coder filed but using fallback main.py")

        # Tester'a GÜVENLİ veri gönder
        test_res = await workflow.execute_activity(
            AgentActivities.tester_run,
            AgentInput(
                task_id,
                current_file,  # ⭐ Artık boş olmayacak
                {
                    'code_content': self.generated_code,
                    'file_path': current_file
                }
            ),
            start_to_close_timeout=timedelta(minutes=2)

        )

        current_file = code_out.file_path
        self.generated_code = code_out.data.get('code_content', '') if code_out.data else ''

        # ---------------------------------------------------------------------
        # AŞAMA 3: SELF-HEALING LOOP (TEST -> DEBUG -> FIX)
        # ---------------------------------------------------------------------
        max_retries = 3
        is_stable = False

        for attempt in range(max_retries):
            workflow.logger.info(f'🔄 Testing Cycle: {attempt + 1}/{max_retries}')

            # Tester'a KOD İÇERİĞİNİ gönder
            test_res = await workflow.execute_activity(
                AgentActivities.tester_run,
                AgentInput(
                    task_id,
                    current_file,
                    {
                        'code_content': self.generated_code,
                        'file_path': current_file
                    }
                ),
                start_to_close_timeout=timedelta(minutes=2)
            )

            if test_res.status == 'success':
                workflow.logger.info('✅ Tests Passed!')
                is_stable = True
                break
            else:
                workflow.logger.error(f'❌ Tests Failed: {test_res.result}')

                # Debugger'a KOD İÇERİĞİNİ gönder
                workflow.logger.info("🚑 Debugger devreye giriyor...")
                fix_out = await workflow.execute_activity(
                    AgentActivities.debugger_fix,
                    AgentInput(
                        task_id,
                        current_file,
                        {
                            'code_content': self.generated_code,
                            'error_log': test_res.result
                        }
                    ),
                    start_to_close_timeout=timedelta(minutes=15)
                )

                # Debugger'dan gelen düzeltilmiş kodu güncelle
                if fix_out.status == 'success' and fix_out.data:
                    self.generated_code = fix_out.data.get('fixed_code', self.generated_code)

        if not is_stable:
            return {'status': 'FAILED', 'reason': 'Max retries exceeded. Code is still broken.'}

        # ---------------------------------------------------------------------
        # AŞAMA 4 & 5: GÜVENLİK VE YAYIN
        # ---------------------------------------------------------------------
        workflow.logger.info("🛡️ Güvenlik ve Yayın Aşaması...")

        # Compliance check
        compliance_res = await workflow.execute_activity(
            AgentActivities.compliance_check,
            AgentInput(
                task_id,
                current_file,
                {'code_content': self.generated_code}
            ),
            start_to_close_timeout=timedelta(minutes=2)
        )

        if compliance_res.status != 'success':
            workflow.logger.warning(f"⚠️ Compliance issues: {compliance_res.result}")

        # Publish
        publish_res = await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(
                task_id,
                current_file,
                {'code_content': self.generated_code}
            ),
            start_to_close_timeout=timedelta(minutes=2)
        )

        workflow.logger.info("✅ SÜREÇ BAŞARIYLA TAMAMLANDI")
        return {
            'status': 'SUCCESS',
            'file': current_file,
            'code_preview': self.generated_code[:500] + "..." if len(
                self.generated_code) > 500 else self.generated_code,
            'prompt_used': self.optimized_prompt,
            'workflow_id': workflow.info().workflow_id
        }

    @workflow.signal
    def override_context(self, data: dict):
        """Kodu manuel olarak düzeltir"""
        new_content = data.get("new_content")
        if new_content:
            self.generated_code = new_content
            workflow.logger.info("⚠️ KOD MANUEL OLARAK DÜZELTİLDİ. YENİ KOD KULLANILACAK.")

    @workflow.signal
    def retry_phase(self, data: dict):
        """Mevcut fazı yeniden dener"""
        workflow.logger.info("🔄 KULLANICI İSTEĞİ ÜZERİNE TEST FAZI YENİDEN TETİKLENİYOR.")