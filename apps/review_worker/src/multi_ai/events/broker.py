from typing import Type, TypeVar, Optional
import logging
import json

from faststream import FastStream, Logger
from faststream.redis import RedisBroker
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type, before_sleep_log

from multi_ai.core.settings import settings, RedisSettings
from .schemas import BaseEvent, GitHubWebhookEvent

logger = logging.getLogger(__name__)

EventT = TypeVar("EventT", bound=BaseEvent)

# --- 1. PUBLISHER (API Gateway'in kullandığı sınıf) ---
class RedisEventBroker:
    _instance: Optional["RedisEventBroker"] = None
    _broker: Optional[RedisBroker] = None
    _is_running: bool = False

    def __init__(self, redis_settings: RedisSettings) -> None:
        self.redis_settings = redis_settings
        if RedisEventBroker._broker is None:
            # Singleton broker instance
            RedisEventBroker._broker = RedisBroker(url=self.redis_settings.url)
        self._broker = RedisEventBroker._broker

    @classmethod
    async def get_instance(cls, redis_settings: Optional[RedisSettings] = None) -> "RedisEventBroker":
        if cls._instance is None:
            if redis_settings is None:
                redis_settings = settings.redis
            cls._instance = RedisEventBroker(redis_settings)
            # Publisher için start() gerekli
            if not cls._instance._is_running:
                await cls._instance._broker.start()
                cls._instance._is_running = True
        return cls._instance

    @retry(
        wait=wait_fixed(1),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def publish(self, event: BaseEvent) -> str:
        msg_id = await self._broker.publish(
            event.model_dump_json(),
            stream=self.redis_settings.stream_key,
            headers={
                "event_type": event.event_type.value,
                "source": event.source,
                "event_id": event.event_id,
                "trace_id": event.trace_id or "",
            },
        )
        logger.info("Published event %s (%s)", event.event_id, event.event_type.value)
        return msg_id

    async def start(self) -> None:
        if not self._is_running:
            await self._broker.start()
            self._is_running = True

    async def stop(self) -> None:
        if self._is_running:
            await self._broker.close()
            self._is_running = False

async def get_event_broker() -> RedisEventBroker:
    return await RedisEventBroker.get_instance()

# --- 2. CONSUMER (Worker'ın kullandığı nesneler) ---
# İŞTE EKSİK OLAN PARÇA BURASIYDI 👇
redis_broker = RedisBroker(url=settings.redis.url)
event_broker_app = FastStream(redis_broker)

@event_broker_app.on_startup
async def _on_startup():
    # Worker başladığında Publisher sistemini de hazırla
    await RedisEventBroker.get_instance()
    logger.info("Event broker app started")

@event_broker_app.on_shutdown
async def _on_shutdown():
    broker = await RedisEventBroker.get_instance()
    await broker.stop()
    logger.info("Event broker app stopped")