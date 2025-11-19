import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from multi_ai.core.settings import settings
from multi_ai.orchestrator.workflows import SupervisorWorkflow
from multi_ai.orchestrator.activities import AgentActivities

# Loglama ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # 1. Temporal Sunucusuna Bağlan
    logger.info(f"🔌 Connecting to Temporal at {settings.temporal.address}...")
    client = await Client.connect(settings.temporal.address, namespace="default")

    # 2. Aktiviteleri (Ajanları) Hazırla
    activities = AgentActivities()

    # 3. Sandbox Runner'ı Oluştur
    runner = SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(
            "multi_ai", "pydantic", "pydantic_settings", "pathlib", "os", "logging", "git", "sqlite3", "cryptography"
        )
    )

    # 4. Worker'ı Kur (TUM AKTIVITELER LISTELENDI)
    worker = Worker(
        client,
        task_queue=settings.temporal.task_queue,
        workflows=[SupervisorWorkflow],
        activities=[
            activities.architect_design, 
            activities.coder_implement,
            activities.publisher_publish,
            activities.compliance_check  # <--- EKLENEN BU!
        ],
        workflow_runner=runner,
    )

    logger.info("🤖 Temporal Worker Started & Listening for workflows (V5.2 ENTERPRISE)...")
    
    # 5. Sonsuza kadar çalış
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
