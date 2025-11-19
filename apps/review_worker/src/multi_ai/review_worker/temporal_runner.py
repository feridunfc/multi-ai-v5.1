import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from multi_ai.core.settings import settings
from multi_ai.orchestrator.workflows import SupervisorWorkflow
from multi_ai.orchestrator.activities import AgentActivities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info(f"🔌 Connecting to Temporal at {settings.temporal.address}...")
    client = await Client.connect(settings.temporal.address, namespace="default")

    activities = AgentActivities()
    
    runner = SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(
            "multi_ai", "pydantic", "pydantic_settings", "pathlib", "os", "logging", "git", "sqlite3", "cryptography", "json"
        )
    )

    worker = Worker(
        client,
        task_queue=settings.temporal.task_queue,
        workflows=[SupervisorWorkflow],
        activities=[
            activities.research_task,      # YENI
            activities.architect_design, 
            activities.coder_implement,
            activities.supervisor_review,  # YENI
            activities.compliance_check,
            activities.publisher_publish
        ],
        workflow_runner=runner,
    )

    logger.info("🤖 Temporal Worker V5.2 Started (ALL SYSTEMS GO)...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
