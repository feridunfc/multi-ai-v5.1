from datetime import timedelta
from temporalio import workflow
from .activities import AgentActivities, AgentInput, AgentOutput

@workflow.defn
class SupervisorWorkflow:
    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Supervisor Workflow Started')

        # 1. ARCHITECT
        architect_output = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(task_id='task_1', instruction='Analyze PR', context=event_payload),
            start_to_close_timeout=timedelta(seconds=60)
        )

        # 2. CODER
        coder_output = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(task_id='task_2', instruction=architect_output.result, context={}),
            start_to_close_timeout=timedelta(seconds=120)
        )
        
        # 3. PUBLISHER (YENİ ADIM)
        # Coder'ın ürettiği dosya yolunu (file_path) input olarak veriyoruz
        publisher_output = await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(task_id='task_3', instruction=coder_output.file_path, context={}),
            start_to_close_timeout=timedelta(seconds=30)
        )

        workflow.logger.info('✅ Workflow Cycle Complete')
        return {
            'architect': architect_output.result, 
            'code_location': coder_output.file_path,
            'git_status': publisher_output.result
        }
