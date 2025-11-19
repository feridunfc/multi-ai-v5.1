from datetime import timedelta
from temporalio import workflow
from .activities import AgentActivities, AgentInput, AgentOutput

@workflow.defn
class SupervisorWorkflow:
    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info("🚀 Supervisor Workflow Started")

        # 1. ADIM: Mimar (Architect) Planlasın
        # Retry politikası: Hata verirse 10 saniyede bir tekrar dene
        architect_output = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(
                task_id="task_1",
                instruction="Analyze this GitHub PR",
                context=event_payload
            ),
            start_to_close_timeout=timedelta(seconds=60)
        )

        # 2. ADIM: Yazılımcı (Coder) Kodlasın
        coder_output = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(
                task_id="task_2",
                instruction=f"Implement this design: {architect_output.result}",
                context={}
            ),
            start_to_close_timeout=timedelta(seconds=60)
        )

        workflow.logger.info("✅ Workflow Finished Successfully")
        return {
            "architect": architect_output.result,
            "code": coder_output.result
        }