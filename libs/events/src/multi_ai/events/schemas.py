from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import uuid


class EventType(str, Enum):
    GITHUB_WEBHOOK = "github.webhook"
    WORKFLOW_TRIGGERED = "workflow.triggered"
    ARCHITECT_ACTIVITY_COMPLETED = "agent.architect.completed"


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    trace_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class GitHubWebhookEvent(BaseEvent):
    event_type: EventType = Field(default=EventType.GITHUB_WEBHOOK, frozen=True)
    github_event_name: str
    github_delivery_id: str
    repository_full_name: str
    pull_request_id: Optional[int] = None
    commit_sha: Optional[str] = None
