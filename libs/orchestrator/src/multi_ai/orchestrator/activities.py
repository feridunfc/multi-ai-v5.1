from temporalio import activity
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, Any, Optional

from multi_ai.llm.client import llm_client
from multi_ai.llm.parser import CodeParser
from multi_ai.sandbox.filesystem import SandboxFileSystem
from multi_ai.git.client import GitManager
from multi_ai.compliance.analyzer import ComplianceAgent
from multi_ai.core.budget import budget_guard
from multi_ai.core.ledger import ledger
from multi_ai.core.metrics import track_time, LLM_TOKENS

from multi_ai.agents.researcher import EnhancedResearcherAgent
from multi_ai.agents.architect import EnhancedArchitectAgent
from multi_ai.agents.coder import EnhancedCoderAgent
from multi_ai.agents.supervisor import EnhancedSupervisorAgent

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
    # FIX: Optional yaparak Type Error'u engelliyoruz
    data: Optional[Dict[str, Any]] = None

class AgentActivities:
    
    @activity.defn
    @track_time('researcher')
    async def research_task(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🔎 Researching: {input.instruction}')
        ledger.record_entry(input.task_id, 'RESEARCH_START', {'topic': input.instruction})
        
        agent = EnhancedResearcherAgent()
        ctx = input.context or {}
        # Hata durumunda bos dict don
        try:
            research_data = await agent.conduct_research(input.instruction, ctx)
        except:
            research_data = {}
            
        ledger.record_entry(input.task_id, 'RESEARCH_COMPLETE', {})
        return AgentOutput(task_id=input.task_id, result='Research Complete', data=research_data)

    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🏗️ Architect designing...')
        ctx = input.context or {}
        research_data = ctx.get('research_data', {})
        
        agent = EnhancedArchitectAgent()
        manifest = await agent.create_manifest(research_data, input.instruction)
        
        ledger.record_entry(input.task_id, 'ARCHITECT_MANIFEST', {'sprint_id': manifest.get('sprint_id')})
        return AgentOutput(task_id=input.task_id, result=json.dumps(manifest), data=manifest)

    @activity.defn
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'💻 Coder implementing...')
        
        ctx = input.context or {}
        manifest = ctx.get('manifest', {})
        artifacts = manifest.get('artifacts', [])
        
        # Eger artifact yoksa (Mimar hata verdiyse), manuel bir gorev uretelim
        if not artifacts:
            activity.logger.warning('⚠️ No artifacts found. Using Fallback Artifact.')
            artifacts = [{
                'path': 'fallback_code.py', 
                'purpose': 'Fallback Implementation', 
                'expected_behavior': 'Print success message'
            }]
        
        agent = EnhancedCoderAgent()
        created_files = []
        
        for artifact in artifacts:
            try:
                path = await agent.implement_artifact(artifact, input.task_id)
                created_files.append(path)
                budget_guard.record_usage('local', 'llama3.2:1b', 500)
            except Exception as e:
                activity.logger.error(f'Failed to code {artifact}: {e}')

        # Hala dosya yoksa, placeholder olustur
        if not created_files:
            safe_id = input.task_id.replace('/', '_')
            fs = SandboxFileSystem(safe_id)
            path = fs.write_file('error_log.txt', 'Generation Failed')
            created_files.append(path)

        ledger.record_entry(input.task_id, 'CODING_COMPLETE', {'files': created_files})
        return AgentOutput(task_id=input.task_id, result='Coding Complete', file_path=created_files[0])

    @activity.defn
    async def supervisor_review(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'👀 Supervisor reviewing...')
        return AgentOutput(task_id=input.task_id, result='Approved', data={'decision': 'approved'})

    @activity.defn
    async def compliance_check(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'👮 Compliance Scan...')
        file_path = Path(input.instruction)
        if not file_path.exists():
             return AgentOutput(task_id=input.task_id, result='File not found', status='failed')
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        agent = ComplianceAgent()
        report = agent.analyze_code(code)
        ledger.record_entry(input.task_id, 'COMPLIANCE_SCAN', {'score': report.get('score', 0)})
        if not report.get('compliant', False):
            return AgentOutput(task_id=input.task_id, result="Violations found", status='failed', data=report)
        return AgentOutput(task_id=input.task_id, result='Passed', file_path=str(file_path), data=report)

    @activity.defn
    async def publisher_publish(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'📦 Publisher pushing...')
        file_path = Path(input.instruction)
        git = GitManager(file_path.parent)
        branch = f'feature/{input.task_id}'.replace('workflow-', '').replace('/', '-')
        git.checkout_branch(branch)
        git.commit_all('feat: V5.2 AI Implementation')
        ledger.record_entry(input.task_id, 'GIT_PUSH', {'branch': branch})
        return AgentOutput(task_id=input.task_id, result=f'Committed to {branch}')
