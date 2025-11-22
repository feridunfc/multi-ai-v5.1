import asyncio
import logging
import sys
import os
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions


# --- CRITICAL FIX: YOLLARI AYARLA ---
def setup_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../../../"))

    manual_paths = [
        os.path.join(project_root, "libs", "utils", "src"),
        os.path.join(project_root, "libs", "agents", "src"),
        os.path.join(project_root, "libs", "orchestrator", "src"),
        os.path.join(project_root, "libs", "core", "src"),
        os.path.join(project_root, "libs", "llm", "src"),
        os.path.join(project_root, "libs", "rag", "src"),
        os.path.join(project_root, "libs", "compliance", "src"),
        os.path.join(project_root, "libs", "sandbox", "src"),
        os.path.join(project_root, "libs", "git", "src"),
    ]
    for p in manual_paths:
        if p not in sys.path:
            sys.path.insert(0, p)


setup_paths()  # En başta çağırılmalı

# --- KRİTİK IMPORTLAR ---
from multi_ai.core.settings import settings
from multi_ai.orchestrator.workflows import SupervisorWorkflow
from multi_ai.orchestrator.activities import AgentActivities
from multi_ai.utils.robust_ollama_client import RobustOllamaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🚀 Worker Başlatılıyor...")

    # 1. Ollama Bağlantı Testi (Gereksiz 404'ü önler)
    try:
        client = RobustOllamaClient()
        await client.generate(model="llama3.2:1b", prompt="ping", options={"num_ctx": 1})
        logger.info("✅ Ollama Bağlantısı BAŞARILI!")
    except Exception as e:
        logger.error(f"❌ Ollama Bağlantı Hatası: {e}")
        return

    # 2. Temporal Client ve Worker
    client = await Client.connect(settings.temporal.address, namespace="default")
    activities = AgentActivities()

    # Sandbox kısıtlamaları (Code Execution için şart)
    runner = SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(
            "multi_ai", "pydantic", "pathlib", "os", "logging", "sys"
        )
    )

    # ⭐ DÜZELTME: prompt_optimize activity'sini EKLE
    worker = Worker(
        client,
        task_queue=settings.temporal.task_queue,
        workflows=[SupervisorWorkflow],
        activities=[
            activities.prompt_optimize,      # ⭐ YENİ: Prompt Agent
            activities.research_task,
            activities.architect_design,
            activities.coder_implement,
            activities.tester_run,
            activities.debugger_fix,
            activities.compliance_check,
            activities.publisher_publish
        ],
        workflow_runner=runner,
    )

    logger.info(f"🤖 Temporal Worker Hazır! Kuyruk: {settings.temporal.task_queue}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())