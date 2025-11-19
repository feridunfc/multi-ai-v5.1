from datetime import timedelta
from temporalio import workflow
from .activities import AgentActivities, AgentInput

@workflow.defn
class SupervisorWorkflow:
    @workflow.run
    async def run(self, event_payload: dict) -> dict:
        workflow.logger.info('🚀 V5.2 Enterprise Workflow Started')
        
        pr_title = event_payload.get('pull_request', {}).get('title', 'Unknown Task')
        task_id = 'task_1'

        # 1. RESEARCHER
        res_out = await workflow.execute_activity(
            AgentActivities.research_task,
            AgentInput(task_id=task_id, instruction=pr_title, context=event_payload),
            start_to_close_timeout=timedelta(seconds=60)
        )

        # 2. ARCHITECT (Research verisiyle)
        arch_out = await workflow.execute_activity(
            AgentActivities.architect_design,
            AgentInput(
                task_id=task_id, 
                instruction=pr_title, 
                context={'research_data': res_out.data}
            ),
            start_to_close_timeout=timedelta(seconds=60)
        )

        # 3. CODER (Manifest verisiyle)
        code_out = await workflow.execute_activity(
            AgentActivities.coder_implement,
            AgentInput(
                task_id=task_id, 
                instruction='Implement manifest', 
                context={'manifest': arch_out.data}
            ),
            start_to_close_timeout=timedelta(seconds=180)
        )
        
        if code_out.status == 'failed':
             raise Exception(f'Coding Failed: {code_out.result}')

        # 4. SUPERVISOR (Kalite Kontrol)
        sup_out = await workflow.execute_activity(
            AgentActivities.supervisor_review,
            AgentInput(
                task_id=task_id, 
                instruction=pr_title, 
                context={'manifest': arch_out.data, 'code_path': code_out.file_path}
            ),
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        if sup_out.status == 'failed':
             return {'status': 'REJECTED_BY_SUPERVISOR', 'reason': sup_out.result}

        # 5. COMPLIANCE (Guvenlik)
        comp_out = await workflow.execute_activity(
            AgentActivities.compliance_check,
            AgentInput(task_id=task_id, instruction=code_out.file_path, context={}),
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        if comp_out.status == 'failed':
             return {'status': 'SECURITY_BLOCKED', 'reason': comp_out.result}

        # 6. PUBLISHER
        pub_out = await workflow.execute_activity(
            AgentActivities.publisher_publish,
            AgentInput(task_id=task_id, instruction=code_out.file_path, context={}),
            start_to_close_timeout=timedelta(seconds=30)
        )

        workflow.logger.info('✅ V5.2 Mission Complete')
        return {'status': 'SUCCESS', 'git': pub_out.result}
