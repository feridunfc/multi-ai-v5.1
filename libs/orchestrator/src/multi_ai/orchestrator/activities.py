from temporalio import activity
from dataclasses import dataclass
from pathlib import Path
from multi_ai.llm.client import llm_client
from multi_ai.llm.parser import CodeParser
from multi_ai.sandbox.filesystem import SandboxFileSystem
from multi_ai.git.client import GitManager

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
    # --- 1. ARCHITECT ---
    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🏗️ Architect is analyzing task: {input.task_id}')
        
        pr_title = input.context.get('payload', {}).get('pull_request', {}).get('title', 'Unknown')
        pr_body = input.context.get('payload', {}).get('pull_request', {}).get('body', 'No content')
        
        user_prompt = f'''REQ: {pr_title}. DETAIL: {pr_body}. TASK: Create a technical implementation plan.'''
        
        try:
            ai_response = await llm_client.generate(prompt=user_prompt, system_prompt='You are a Senior Software Architect.')
        except Exception as e:
            ai_response = f'Error: {str(e)}'
            
        return AgentOutput(task_id=input.task_id, result=ai_response)

    # --- 2. CODER ---
    @activity.defn
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'💻 Coder is working on task: {input.task_id}')
        
        user_prompt = f'''PLAN: {input.instruction}. TASK: Write Python code. Provide ONLY the code block.'''
        
        try:
            raw_response = await llm_client.generate(prompt=user_prompt, system_prompt='You are an Expert Python Developer.')
            clean_code = CodeParser.extract_python_code(raw_response)
            
            safe_task_id = input.task_id.replace('/', '_').replace('-', '_')
            sandbox = SandboxFileSystem(task_id=safe_task_id)
            file_path = sandbox.write_file('generated_code.py', clean_code)
            
            return AgentOutput(task_id=input.task_id, result=f'Code saved to: {file_path}', file_path=file_path)
        except Exception as e:
            return AgentOutput(task_id=input.task_id, result=f'Error: {str(e)}', status='failed')

    # --- 3. PUBLISHER (YENİ) ---
    @activity.defn
    async def publisher_publish(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'📦 Publisher is processing: {input.task_id}')
        
        try:
            # Dosyanın oldugu klasoru bir Git Reposu yapalim
            # Not: Gercek senaryoda buraya git clone yapilir.
            # Simdilik Sandbox'i local repo yapiyoruz.
            
            file_path = Path(input.instruction) # Coder'dan dosya yolu geliyor
            repo_path = file_path.parent
            
            git = GitManager(repo_path)
            
            # Branch ac ve commitla
            branch_name = f'feature/{input.task_id}'.replace('workflow-', '').replace('/', '-')
            git.checkout_branch(branch_name)
            git.commit_all(f'feat: AI Implementation for {input.task_id}')
            
            # Push (Opsiyonel - Auth gerektirir, simdilik log basiyoruz)
            # git.push(branch_name) 
            
            msg = f'✅ Changes committed to branch: {branch_name} in {repo_path}'
            activity.logger.info(msg)
            return AgentOutput(task_id=input.task_id, result=msg)
            
        except Exception as e:
            activity.logger.error(f'Publisher Failed: {e}')
            return AgentOutput(task_id=input.task_id, result=f'Publisher Error: {str(e)}', status='failed')
