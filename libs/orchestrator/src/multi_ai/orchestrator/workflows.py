from datetime import timedelta
from temporalio import workflow
# Importlar (Activities sinifi icinden string referansla cagrilabilir ama biz class kullaniyoruz)
from .activities import AgentActivities, AgentInput, AgentOutput

@workflow.defn
class SupervisorWorkflow:
    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Supervisor Workflow Started (V5.2 Security Enabled)')

        # 1. ADIM: MIMAR (ARCHITECT)
        architect_output = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(task_id='task_1', instruction='Analyze PR', context=event_payload),
            start_to_close_timeout=timedelta(seconds=60)
        )

        # 2. ADIM: YAZILIMCI (CODER)
        coder_output = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(task_id='task_2', instruction=architect_output.result, context={}),
            start_to_close_timeout=timedelta(seconds=120)
        )
        
        # 3. ADIM: GÜVENLİK POLİSİ (COMPLIANCE GATE) - KRİTİK ADIM
        compliance_output = await workflow.execute_activity(
            AgentActivities.compliance_check,
            AgentInput(task_id='task_3', instruction=coder_output.file_path, context={}),
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Eger guvenlikten gecemezse, workflow burada biter!
        if compliance_output.status == 'failed':
            workflow.logger.error(f'🛑 SECURITY BLOCK: {compliance_output.result}')
            return {
                'status': 'FAILED',
                'reason': 'Security Violation',
                'details': compliance_output.result
            }

        # 4. ADIM: YAYINCI (PUBLISHER) - Sadece guvenli kod buraya ulasir
        publisher_output = await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(task_id='task_4', instruction=coder_output.file_path, context={}),
            start_to_close_timeout=timedelta(seconds=30)
        )

        workflow.logger.info('✅ Workflow Cycle Complete (SECURE)')
        return {
            'architect': architect_output.result, 
            'compliance': 'PASSED',
            'git_status': publisher_output.result
        }
