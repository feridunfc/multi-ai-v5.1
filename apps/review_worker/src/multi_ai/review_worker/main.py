import logging
import asyncio
from typing import Union
from faststream import Logger
from temporalio.client import Client

from multi_ai.core.settings import settings
from multi_ai.events.schemas import GitHubWebhookEvent
from multi_ai.events.broker import event_broker_app, RedisEventBroker, redis_broker

logger = logging.getLogger(__name__)
temporal_client = None


@event_broker_app.on_startup
async def setup_temporal():
    global temporal_client
    try:
        temporal_client = await Client.connect(settings.temporal.address, namespace="default")
        logger.info("✅ Connected to Temporal Server")
    except Exception as e:
        logger.error(f"❌ Could not connect to Temporal: {e}")


# DÜZELTME: 'message' yerine 'body' alıyoruz ve tipini esnek bırakıyoruz (str veya dict)
@redis_broker.subscriber(stream=settings.redis.stream_key)
async def handle_github_webhook(body: Union[str, dict], logger: Logger):
    # 1. Manuel Parse (Validation Fix)
    try:
        if isinstance(body, str):
            # Eğer String geldiyse JSON olarak parse et
            message = GitHubWebhookEvent.model_validate_json(body)
        else:
            # Eğer Dict geldiyse direkt doğrula
            message = GitHubWebhookEvent.model_validate(body)
    except Exception as e:
        logger.error(f"🔥 Payload Validation Failed: {e}")
        return

    logger.info(
        "📩 Received GitHub event: %s (Repo: %s)",
        message.github_event_name,
        message.repository_full_name,
    )

    if not temporal_client:
        logger.error("Temporal client not ready!")
        return

    # 2. Temporal Trigger
    try:
        workflow_id = f"workflow-{message.repository_full_name}-{message.pull_request_id}"

        handle = await temporal_client.start_workflow(
            "SupervisorWorkflow",
            message.model_dump(),
            id=workflow_id,
            task_queue=settings.temporal.task_queue,
        )
        logger.info(f"🚀 Workflow started! ID: {handle.id} RunID: {handle.result_run_id}")

    except Exception as e:
        logger.error(f"🔥 Failed to start workflow: {e}")


if __name__ == "__main__":
    asyncio.run(event_broker_app.run())