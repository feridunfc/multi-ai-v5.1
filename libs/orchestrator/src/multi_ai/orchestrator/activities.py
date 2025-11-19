from temporalio import activity
from dataclasses import dataclass
from multi_ai.llm.client import llm_client
from multi_ai.llm.parser import CodeParser
from multi_ai.sandbox.filesystem import SandboxFileSystem

@dataclass
class AgentInput:
    task_id: str
    instruction: str
    context: dict

@dataclass
class AgentOutput:
    task_id: str
    result: str
    status: str = 'success'
    file_path: str = ''

class AgentActivities:
    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🏗️ Architect is analyzing task: {input.task_id}')
        
        pr_title = input.context.get('payload', {}).get('pull_request', {}).get('title', 'Unknown')
        pr_body = input.context.get('payload', {}).get('pull_request', {}).get('body', 'No content')
        
        user_prompt = f'''
        REQ: {pr_title}
        DETAIL: {pr_body}
        TASK: Create a technical implementation plan.
        '''
        
        try:
            ai_response = await llm_client.generate(
                prompt=user_prompt, 
                system_prompt='You are a Senior Software Architect. Provide a short, clear implementation plan.'
            )
        except Exception as e:
            ai_response = f'Architect Error: {str(e)}'
        
        activity.logger.info('✅ Architect plan generated.')
        return AgentOutput(task_id=input.task_id, result=ai_response)

    @activity.defn
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'💻 Coder is working on task: {input.task_id}')
        
        # 1. Kodu Üret
        user_prompt = f'''
        ARCHITECT PLAN:
        {input.instruction}
        
        TASK: Write the Python code. Provide ONLY the code block.
        '''
        
        try:
            raw_response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt='You are an Expert Python Developer. Write clean code.'
            )
            
            # 2. Kodu Temizle
            clean_code = CodeParser.extract_python_code(raw_response)
            
            # 3. Dosyaya Kaydet (Sandbox)
            # Task ID'yi dosya sistemi dostu hale getir
            safe_task_id = input.task_id.replace('/', '_').replace('-', '_')
            sandbox = SandboxFileSystem(task_id=safe_task_id)
            
            file_path = sandbox.write_file('generated_code.py', clean_code)
            
            result_msg = f'Code saved to: {file_path}'
            activity.logger.info(f'✅ {result_msg}')
            
            return AgentOutput(
                task_id=input.task_id, 
                result=result_msg,
                file_path=file_path
            )
            
        except Exception as e:
            err_msg = f'Coder Error: {str(e)}'
            activity.logger.error(err_msg)
            return AgentOutput(task_id=input.task_id, result=err_msg, status='failed')
