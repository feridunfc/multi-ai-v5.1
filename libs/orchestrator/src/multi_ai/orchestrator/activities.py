from temporalio import activity
from dataclasses import dataclass
from pathlib import Path
import json

from multi_ai.llm.client import llm_client
from multi_ai.llm.parser import CodeParser
from multi_ai.sandbox.filesystem import SandboxFileSystem
from multi_ai.git.client import GitManager
from multi_ai.compliance.analyzer import ComplianceAgent
from multi_ai.core.budget import budget_guard
from multi_ai.core.ledger import ledger
from multi_ai.core.metrics import track_time, LLM_TOKENS

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
    @track_time('architect')
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🏗️ Enhanced Architect analyzing: {input.task_id}')
        ledger.record_entry(input.task_id, 'ARCHITECT_START', {'instruction': input.instruction})
        
        pr_title = input.context.get('payload', {}).get('pull_request', {}).get('title', 'Unknown')
        pr_body = input.context.get('payload', {}).get('pull_request', {}).get('body', 'No content')

        # Gelişmiş Prompt (Senin architect.py dosyan baz alinarak)
        user_prompt = f'''
        ROLE: Senior Software Architect
        GOAL: Analyze PR '{pr_title}' and create a implementation manifest.
        DETAILS: {pr_body}
        
        OUTPUT JSON FORMAT:
        {{
            "analysis": "Technical analysis...",
            "plan": ["step 1", "step 2"],
            "risk_level": "low|medium|high",
            "files_to_change": ["filename.py"]
        }}
        '''
        
        try:
            ai_response = await llm_client.generate(prompt=user_prompt, system_prompt='You are an Architect. Reply in JSON.')
            # JSON Parsing
            try:
                plan_data = json.loads(ai_response)
                formatted_result = json.dumps(plan_data, indent=2)
            except:
                formatted_result = ai_response

            budget_guard.record_usage('local', 'llama3.2:1b', len(ai_response))
            LLM_TOKENS.labels(model='llama3.2:1b', provider='ollama').inc(len(ai_response))
            
            ledger.record_entry(input.task_id, 'ARCHITECT_COMPLETE', {'plan': formatted_result})
            return AgentOutput(task_id=input.task_id, result=formatted_result)
            
        except Exception as e:
            return AgentOutput(task_id=input.task_id, result=str(e), status='failed')

    @activity.defn
    @track_time('coder')
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'💻 Enhanced Coder working...')
        ledger.record_entry(input.task_id, 'CODER_START', {})
        
        user_prompt = f'''
        ARCHITECT PLAN:
        {input.instruction}
        
        TASK: Implement the code securely. 
        REQUIREMENTS:
        - Follow PEP8
        - Include docstrings
        - NO hardcoded secrets
        '''
        
        try:
            raw_response = await llm_client.generate(prompt=user_prompt, system_prompt='You are a Senior Python Dev.')
            clean_code = CodeParser.extract_python_code(raw_response)
            
            safe_task_id = input.task_id.replace('/', '_').replace('-', '_')
            sandbox = SandboxFileSystem(task_id=safe_task_id)
            file_path = sandbox.write_file('generated_code.py', clean_code)
            
            ledger.record_entry(input.task_id, 'CODER_COMPLETE', {'file': file_path})
            return AgentOutput(task_id=input.task_id, result='Code saved', file_path=file_path)
        except Exception as e:
            return AgentOutput(task_id=input.task_id, result=f'Error: {str(e)}', status='failed')

    @activity.defn
    @track_time('compliance')
    async def compliance_check(self, input: AgentInput) -> AgentOutput:
        # (Önceki kodun aynisi, sadece Ledger ekliyoruz)
        activity.logger.info(f'👮 Compliance Scan...')
        file_path = Path(input.instruction)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        agent = ComplianceAgent()
        report = agent.analyze_code(code)
        
        ledger.record_entry(input.task_id, 'COMPLIANCE_SCAN', report)
        
        if not report['compliant']:
            msg = f"❌ VIOLATIONS: {len(report['violations'])}"
            return AgentOutput(task_id=input.task_id, result=msg, status='failed')
            
        return AgentOutput(task_id=input.task_id, result='Passed', status='success', file_path=str(file_path))

    @activity.defn
    async def publisher_publish(self, input: AgentInput) -> AgentOutput:
        # (Ayni kalabilir, ledger ekle)
        activity.logger.info(f'📦 Publisher processing...')
        file_path = Path(input.instruction)
        git = GitManager(file_path.parent)
        
        branch = f'feature/{input.task_id}'.replace('workflow-', '').replace('/', '-')
        git.checkout_branch(branch)
        git.commit_all('feat: Enterprise AI Auto-Code')
        
        ledger.record_entry(input.task_id, 'GIT_PUSH', {'branch': branch})
        return AgentOutput(task_id=input.task_id, result=f'Committed to {branch}')
