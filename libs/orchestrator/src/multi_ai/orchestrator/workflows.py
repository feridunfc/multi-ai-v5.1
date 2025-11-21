from datetime import timedelta
from temporalio import workflow
from .activities import AgentActivities, AgentInput

@workflow.defn
class SupervisorWorkflow:
    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 Sprint 7: Self-Healing Workflow Started')
        task_id = 'task_auto'
        title = event_payload.get('pull_request', {}).get('title', 'Task')

        # 1. PLANLAMA (Researcher -> Architect)
        res = await workflow.execute_activity(AgentActivities.research_task, AgentInput(task_id, title, event_payload), start_to_close_timeout=timedelta(seconds=60))
        arch = await workflow.execute_activity(AgentActivities.architect_design, AgentInput(task_id, title, {'research_data': res.data}), start_to_close_timeout=timedelta(seconds=60))
        
        # 2. KODLAMA
        code_out = await workflow.execute_activity(AgentActivities.coder_implement, AgentInput(task_id, 'Implement', {'manifest': arch.data}), start_to_close_timeout=timedelta(seconds=120))
        current_file = code_out.file_path

        # 3. SELF-HEALING LOOP (Test -> Debug -> Fix)
        max_retries = 3
        is_stable = False
        
        for attempt in range(max_retries):
            workflow.logger.info(f'🔄 Testing Cycle: {attempt + 1}/{max_retries}')
            
            # Test Et
            test_res = await workflow.execute_activity(
                AgentActivities.tester_run, 
                AgentInput(task_id, current_file, {}), 
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            if test_res.status == 'success':
                workflow.logger.info('✅ Tests Passed!')
                is_stable = True
                break
            else:
                workflow.logger.error(f'❌ Tests Failed: {test_res.result}')
                # Debug Et ve Duzelt
                fix_out = await workflow.execute_activity(
                    AgentActivities.debugger_fix,
                    AgentInput(task_id, current_file, {'error_log': test_res.result}),
                    start_to_close_timeout=timedelta(seconds=120)
                )
                # Dosya yolunu guncelle (Ayni dosya ama icerik degisti)
                current_file = fix_out.file_path

        if not is_stable:
            return {'status': 'FAILED', 'reason': 'Max retries exceeded. Code is still broken.'}

        # 4. GÜVENLİK (Compliance)
        comp = await workflow.execute_activity(AgentActivities.compliance_check, AgentInput(task_id, current_file, {}), start_to_close_timeout=timedelta(seconds=30))
        if comp.status == 'failed':
            return {'status': 'BLOCKED', 'reason': comp.result}

        # 5. YAYIN (Publisher)
        pub = await workflow.execute_activity(AgentActivities.publisher_publish, AgentInput(task_id, current_file, {}), start_to_close_timeout=timedelta(seconds=30))

        return {'status': 'SUCCESS', 'file': current_file}
