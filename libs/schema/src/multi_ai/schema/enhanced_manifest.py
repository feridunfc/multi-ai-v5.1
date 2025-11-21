from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import hashlib
import json

class ArtifactType(str, Enum):
    CODE = "code"
    TEST = "test"
    DOCUMENTATION = "documentation"
    CONFIG = "configuration"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(BaseModel):
    level: RiskLevel
    factors: List[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)

class Artifact(BaseModel):
    artifact_id: str
    type: ArtifactType
    path: str
    purpose: str
    expected_behavior: str = ""
    risk_assessment: RiskAssessment
    estimated_effort: float = 0.0

class SprintManifest(BaseModel):
    sprint_id: str
    sprint_purpose: str
    version: str = "5.2"
    artifacts: List[Artifact]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def calculate_manifest_hash(self) -> str:
        data = self.model_dump(mode="json")
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
