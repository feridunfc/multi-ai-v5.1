import logging
from temporalio import activity
from dataclasses import dataclass, field
from pathlib import Path
import json
import os
from typing import Dict, Any, Optional

# Ledger import'unu düzelt - SignedLedger kullan
from multi_ai.core.ledger import SignedLedger

# Ajanlar
from multi_ai.agents.researcher import EnhancedResearcherAgent
from multi_ai.agents.architect import EnhancedArchitectAgent
from multi_ai.agents.coder import EnhancedCoderAgent
from multi_ai.agents.tester import EnhancedTesterAgent
from multi_ai.agents.debugger import EnhancedDebuggerAgent
from multi_ai.agents.prompt_agent import EnhancedPromptAgent

logger = logging.getLogger(__name__)


@dataclass
class AgentInput:
    activity_id: str
    instruction: str
    metadata: dict = field(default_factory=dict)
    code_content: str = ""


@dataclass
class AgentOutput:
    activity_id: str
    status: str = 'success'
    data: Dict[str, Any] = field(default_factory=dict)
    file_path: str = ''
    result: str = ''


class AgentActivities:
    def __init__(self):
        # SignedLedger instance'ını kullan
        self.ledger = SignedLedger()

    @activity.defn
    async def prompt_optimize(self, input: AgentInput) -> AgentOutput:
        """Prompt optimizasyonu yapar"""
        try:
            agent = EnhancedPromptAgent()

            context = {
                "workflow_type": "software_development",
                "target_language": "python",
                "required_libraries": ["standard library only"],
                "quality_requirements": ["production_ready", "well_tested", "user_friendly"]
            }

            result = await agent.optimize_prompt(input.instruction, context)

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="PROMPT_OPTIMIZATION",
                data={
                    "agent_type": "PROMPT_ENGINEER",
                    "original_prompt": input.instruction,
                    "optimized_prompt": result.get("optimized_prompt", ""),
                    "complexity": result.get("estimated_complexity", "unknown"),
                    "file_path": "prompt_optimization.json"
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data=result,
                file_path="prompt_optimization.json"
            )

        except Exception as e:
            logger.error(f"Prompt optimization error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )

    @activity.defn
    async def research_task(self, input: AgentInput) -> AgentOutput:
        """Research ajanını çalıştırır"""
        activity.logger.info(f'🔎 Researcher starting task: {input.activity_id}')
        try:
            agent = EnhancedResearcherAgent()
            research_data = await agent.conduct_research(input.instruction)

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="RESEARCH_TASK",
                data={
                    "agent_type": "RESEARCHER",
                    "query": input.instruction,
                    "file_path": "research.json"
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data=research_data,
                file_path="research.json"
            )
        except Exception as e:
            logger.error(f"Research error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )

    @activity.defn
    async def architect_design(self, input: AgentInput) -> AgentOutput:
        """Architect ajanını çalıştırır"""
        activity.logger.info(f'🏗️ Architect designing: {input.activity_id}')
        try:
            research_data = input.metadata.get('research_data', {})
            agent = EnhancedArchitectAgent()
            manifest = await agent.create_manifest(research_data, input.instruction)

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="ARCHITECT_DESIGN",
                data={
                    "agent_type": "ARCHITECT",
                    "file_path": "manifest.json"
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data=manifest,
                file_path="manifest.json"
            )
        except Exception as e:
            logger.error(f"Architect error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )

    @activity.defn

    async def coder_implement(self, input: AgentInput) -> AgentOutput:
        """Coder ajanını çalıştırır - GÜVENLİ VERSİYON"""
        activity.logger.info(f'💻 Coder implementing: {input.activity_id}')
        try:
            manifest = input.metadata.get('manifest', {})
            artifacts = manifest.get('artifacts', [])

            # ⭐ KRİTİK: Manifest kontrolü
            if not artifacts:
                artifacts = [{
                    'path': 'main.py',
                    'purpose': 'Main application',
                    'instructions': input.instruction
                }]
                activity.logger.warning("⚠️ No artifacts in manifest, using default main.py")

            agent = EnhancedCoderAgent()
            created_files = []
            last_code_content = ""

            for artifact in artifacts:
                # ⭐ GÜVENLİ PATH OLUŞTURMA
                file_path = artifact.get('path', '').strip()
                if not file_path:
                    file_path = 'main.py'
                    activity.logger.warning(f"⚠️ Empty path, using: {file_path}")

                # Dosya adı güvenli mi kontrol et
                if not file_path.endswith('.py'):
                    file_path += '.py'
                    activity.logger.info(f"📝 Added .py extension: {file_path}")

                # Kodu üret
                activity.logger.info(f"📄 Generating code for: {file_path}")
                code_content = await agent.implement_artifact(artifact, input.activity_id)
                last_code_content = code_content  # Son kodu sakla

                # ⭐ DİZİN OLUŞTURMA
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    activity.logger.info(f"📁 Directory created: {directory}")

                # Kodu dosyaya yaz
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code_content)

                created_files.append(file_path)
                activity.logger.info(f"✅ File created: {file_path} ({len(code_content)} chars)")

                # Ledger kaydı
                self.ledger.record_entry(
                    sprint_id=input.activity_id,
                    action="CODE_IMPLEMENT",
                    data={
                        "agent_type": "CODER",
                        "file": file_path,
                        "purpose": artifact.get('purpose', ''),
                        "file_path": file_path,
                        "content_length": len(code_content)
                    }
                )

            main_file = created_files[0] if created_files else 'main.py'

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data={
                    "files": created_files,
                    "code_content": last_code_content,
                    "main_file": main_file
                },
                file_path=main_file,
                result=f"Coded {len(created_files)} files"
            )

        except Exception as e:
            logger.error(f"Coder error: {e}")
            # Hata durumunda bile boş path dönme
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path="main.py"  # ⭐ Fallback path
            )

    @activity.defn
    async def tester_run(self, input: AgentInput) -> AgentOutput:
        """Test ajanını çalıştırır"""
        activity.logger.info(f'🧪 Tester running: {input.activity_id}')
        try:
            agent = EnhancedTesterAgent()

            # Kod içeriğini al
            if input.code_content:
                code_to_test = input.code_content
                file_name = input.instruction
            elif input.instruction and os.path.exists(input.instruction):
                with open(input.instruction, 'r', encoding='utf-8') as f:
                    code_to_test = f.read()
                file_name = input.instruction
            else:
                return AgentOutput(
                    activity_id=input.activity_id,
                    status="error",
                    data={"success": False, "output": "No code content or valid file path provided"},
                    file_path=""
                )

            result = agent.run_code(code_to_test, file_name)

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="TEST_RUN",
                data={
                    "agent_type": "TESTER",
                    "success": result["success"],
                    "file": file_name,
                    "file_path": file_name
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success" if result["success"] else "error",
                data=result,
                file_path=file_name,
                result=result.get("output", "")
            )
        except Exception as e:
            logger.error(f"Tester error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"success": False, "output": str(e)},
                file_path=""
            )

    @activity.defn
    async def debugger_fix(self, input: AgentInput) -> AgentOutput:
        """Debugger ajanını çalıştırır"""
        activity.logger.info(f'🚑 Debugger fixing: {input.activity_id}')
        try:
            error_log = input.metadata.get('error_log', '')
            code_content = input.code_content

            agent = EnhancedDebuggerAgent()
            diagnosis = await agent.diagnose_error(code_content, error_log)
            fixed_code = diagnosis.get('fixed_code', code_content)

            # Düzeltilmiş kodu dosyaya yaz
            if input.instruction and os.path.exists(input.instruction):
                with open(input.instruction, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="DEBUG_FIX",
                data={
                    "agent_type": "DEBUGGER",
                    "diagnosis": diagnosis.get("diagnosis", ""),
                    "file_path": input.instruction
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data={"fixed_code": fixed_code, "diagnosis": diagnosis.get("diagnosis", "")},
                file_path=input.instruction,
                result="Fixed"
            )
        except Exception as e:
            logger.error(f"Debugger error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )

    @activity.defn
    async def compliance_check(self, input: AgentInput) -> AgentOutput:
        """Compliance check yapar"""
        activity.logger.info(f'🛡️ Compliance check: {input.activity_id}')
        try:
            code_content = input.code_content

            # Basit güvenlik kontrolleri
            security_issues = []
            dangerous_patterns = [
                "os.system", "subprocess.call", "eval(", "exec(", "__import__", "open("
            ]

            for pattern in dangerous_patterns:
                if pattern in code_content:
                    security_issues.append(f"Potentially dangerous pattern: {pattern}")

            is_compliant = len(security_issues) == 0

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="COMPLIANCE_CHECK",
                data={
                    "agent_type": "COMPLIANCE",
                    "compliant": is_compliant,
                    "issues": security_issues,
                    "file_path": input.instruction
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success" if is_compliant else "error",
                data={"compliant": is_compliant, "issues": security_issues},
                file_path=input.instruction,
                result="Compliant" if is_compliant else f"Issues: {security_issues}"
            )
        except Exception as e:
            logger.error(f"Compliance error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )

    @activity.defn
    async def publisher_publish(self, input: AgentInput) -> AgentOutput:
        """Publisher ajanını çalıştırır"""
        activity.logger.info(f'📦 Publisher publishing: {input.activity_id}')
        try:
            file_path = input.instruction

            # SignedLedger formatında kaydet
            self.ledger.record_entry(
                sprint_id=input.activity_id,
                action="PUBLISH",
                data={
                    "agent_type": "PUBLISHER",
                    "file": file_path,
                    "status": "published",
                    "file_path": file_path
                }
            )

            return AgentOutput(
                activity_id=input.activity_id,
                status="success",
                data={"published": True, "file": file_path},
                file_path=file_path,
                result="Published"
            )
        except Exception as e:
            logger.error(f"Publisher error: {e}")
            return AgentOutput(
                activity_id=input.activity_id,
                status="error",
                data={"error": str(e)},
                file_path=""
            )