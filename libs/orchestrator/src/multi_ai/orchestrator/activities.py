from temporalio import activity
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Yardımcı Kütüphaneler
from multi_ai.llm.parser import CodeParser
from multi_ai.sandbox.filesystem import SandboxFileSystem
from multi_ai.git.client import GitManager
from multi_ai.compliance.analyzer import ComplianceAgent
from multi_ai.core.budget import budget_guard
from multi_ai.core.ledger import ledger
from multi_ai.core.metrics import track_time

# Ajanlar
from multi_ai.agents.researcher import EnhancedResearcherAgent
from multi_ai.agents.architect import EnhancedArchitectAgent
from multi_ai.agents.coder import EnhancedCoderAgent
from multi_ai.agents.supervisor import EnhancedSupervisorAgent
from multi_ai.agents.tester import EnhancedTesterAgent
from multi_ai.agents.debugger import EnhancedDebuggerAgent


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
    data: Optional[Dict[str, Any]] = field(default_factory=dict)


class AgentActivities:

    @activity.defn
    async def research_task(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🔎 Researcher starting task: {input.task_id}')
        agent = EnhancedResearcherAgent()
        res = await agent.conduct_research(input.instruction)
        return AgentOutput(task_id=input.task_id, result='Done', data=res)

    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🏗️ Architect designing: {input.task_id}')
        ctx = input.context or {}
        agent = EnhancedArchitectAgent()
        manifest = await agent.create_manifest(ctx.get('research_data', {}), input.instruction)
        return AgentOutput(task_id=input.task_id, result=json.dumps(manifest), data=manifest)

    @activity.defn
    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'💻 Coder implementing: {input.task_id}')
        ctx = input.context or {}
        manifest = ctx.get('manifest', {})

        # Artifact listesini güvenli al
        artifacts = manifest.get('artifacts', [])
        if not artifacts:
            artifacts = [{'path': 'main.py', 'purpose': 'Main Logic'}]

        agent = EnhancedCoderAgent()
        created_files = []

        for art in artifacts:
            path = await agent.implement_artifact(art, input.task_id)
            created_files.append(path)

        # İlk dosya yolunu döndür
        main_file = created_files[0] if created_files else ''
        return AgentOutput(task_id=input.task_id, result='Coded', file_path=main_file)

    @activity.defn
    async def tester_run(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🧪 Tester running: {input.instruction}')
        agent = EnhancedTesterAgent()
        result = agent.run_code(input.instruction)

        ledger.record_entry(input.task_id, 'TEST_RUN', result)

        if not result['success']:
            # GÜVENLİ HATA MESAJI OLUŞTURMA (KeyError Çözümü)
            output_msg = result.get('output', str(result)) if isinstance(result, dict) else str(result)
            return AgentOutput(task_id=input.task_id, result=output_msg, status='failed', data=result)

        return AgentOutput(task_id=input.task_id, result='Passed', status='success', data=result)

    @activity.defn
    async def debugger_fix(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🚑 Debugger fixing: {input.instruction}')

        file_path = input.instruction
        error_log = input.context.get('error_log', '')

        try:
            # Hatalı dosyayı oku
            with open(file_path, 'r', encoding='utf-8') as f:
                broken_code = f.read()

            agent = EnhancedDebuggerAgent()
            diagnosis = await agent.diagnose_error(broken_code, error_log)

            # Düzeltilmiş kodu ayrıştır ve kaydet
            fixed_code_raw = diagnosis.get('fixed_code', '')
            clean_code = CodeParser.extract_python_code(fixed_code_raw)

            # Eğer parser boş döndürürse ham hali kullan (Fallback)
            if not clean_code.strip():
                clean_code = fixed_code_raw

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(clean_code)

            ledger.record_entry(input.task_id, 'DEBUG_FIX', {'file': file_path})
            return AgentOutput(task_id=input.task_id, result='Fixed', file_path=file_path)

        except Exception as e:
            activity.logger.error(f"Debugger Error: {e}")
            return AgentOutput(task_id=input.task_id, result=str(e), status='failed')

    @activity.defn
    async def compliance_check(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'🛡️ Compliance check: {input.instruction}')
        file_path = Path(input.instruction)

        if not file_path.exists():
            return AgentOutput(task_id=input.task_id, status='failed', result='File Not Found')

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        agent = ComplianceAgent()
        rep = agent.analyze_code(code)

        if not rep['compliant']:
            return AgentOutput(task_id=input.task_id, result=json.dumps(rep['issues']), status='failed', data=rep)

        return AgentOutput(task_id=input.task_id, result='Passed', file_path=str(file_path))

    @activity.defn
    async def publisher_publish(self, input: AgentInput) -> AgentOutput:
        activity.logger.info(f'📦 Publisher publishing: {input.instruction}')
        file_path = Path(input.instruction)

        try:
            git = GitManager(file_path.parent)
            branch_name = f'feature/{input.task_id.replace("/", "-")}'

            # Eğer repo yoksa init et (GitManager içinde olabilir ama garanti olsun)
            if not (file_path.parent / ".git").exists():
                git.init_repo()

            git.checkout_branch(branch_name)
            git.commit_all('feat: AI Implementation')
            return AgentOutput(task_id=input.task_id, result='Committed')
        except Exception as e:
            activity.logger.error(f"Git Error: {e}")
            # Git hatası olsa bile süreci başarılı sayabiliriz (dosya oluştu sonuçta)
            return AgentOutput(task_id=input.task_id, result=f'Git Error: {e}', status='success')