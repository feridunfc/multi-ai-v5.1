import os
from pathlib import Path

def create_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"? Created: {path}")

# ==========================================
# 1. PDF REPORTER (libs/utils)
# ==========================================
pdf_code = """import json
from io import BytesIO
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Title2', parent=self.styles['Heading1'], fontSize=16, spaceAfter=30, textColor=colors.darkblue))

    def _events_table(self, events: List[Dict]):
        headers = ['Time', 'Action', 'Hash']
        data = [headers]
        for e in events:
            try:
                ts = datetime.fromtimestamp(e[0]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                ts = str(e[0])
            data.append([ts, str(e[1]), str(e[2])[:8] + '...'])
            
        t = Table(data, colWidths=[150, 200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        return t

    def generate_ledger_report(self, sprint_id: str) -> str:
        import sqlite3
        db_path = '.cache/ledger.db'
        
        if not os.path.exists(db_path):
            return "No ledger database found."
            
        conn = sqlite3.connect(db_path)
        cursor = conn.execute('SELECT timestamp, action, hash FROM ledger_entries WHERE sprint_id = ?', (sprint_id,))
        events = cursor.fetchall()
        conn.close()

        file_path = f'.cache/report_{sprint_id.replace("/", "_")}.pdf'
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        story.append(Paragraph(f"Audit Report: {sprint_id}", self.styles['Title2']))
        story.append(Spacer(1, 12))
        
        if events:
            story.append(self._events_table(events))
        else:
            story.append(Paragraph("No events found for this sprint.", self.styles['Normal']))
            
        doc.build(story)
        return file_path

pdf_reporter = PDFReporter()
"""
create_file("libs/utils/src/multi_ai/utils/pdf_reporter.py", pdf_code)

# ==========================================
# 2. ENHANCED MANIFEST (libs/schema)
# ==========================================
schema_toml = """[tool.poetry]
name = "multi-ai-schema"
version = "5.2.0"
description = "Data models and schemas"
packages = [{include = "multi_ai", from = "src"}]

[tool.poetry.dependencies]
python = ">=3.11,<3.14"
pydantic = "^2.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
create_file("libs/schema/pyproject.toml", schema_toml)

manifest_code = """from pydantic import BaseModel, Field
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
"""
create_file("libs/schema/src/multi_ai/schema/enhanced_manifest.py", manifest_code)

create_file("libs/schema/src/multi_ai/schema/__init__.py", 
            "from .enhanced_manifest import SprintManifest, Artifact, RiskAssessment, ArtifactType, RiskLevel\n__all__ = ['SprintManifest', 'Artifact', 'RiskAssessment', 'ArtifactType', 'RiskLevel']")

# ==========================================
# 3. HYBRID ROUTER (libs/llm update)
# ==========================================
router_code = """import logging
from typing import Dict, Any
from dataclasses import dataclass
from multi_ai.core.budget import budget_guard

logger = logging.getLogger(__name__)

@dataclass
class RoutingDecision:
    use_cloud: bool
    provider: str
    model: str
    reason: str

class HybridRouter:
    def __init__(self):
        self.local_model = "llama3.2:1b"
        
    def route(self, task_type: str, prompt: str) -> RoutingDecision:
        # Simdilik hep LOCAL
        return RoutingDecision(
            use_cloud=False,
            provider="ollama",
            model=self.local_model,
            reason="Default Local Policy"
        )

    async def complete(self, prompt: str, **kwargs) -> str:
        from .client import llm_client
        
        decision = self.route("general", prompt)
        logger.info(f"Router Decision: {decision.provider}/{decision.model}")
        
        if not budget_guard.check_budget(0.001):
            raise Exception("Budget Exceeded")

        return await llm_client.generate(prompt)

hybrid_router = HybridRouter()
"""
create_file("libs/llm/src/multi_ai/llm/router.py", router_code)

# init update
with open("libs/llm/src/multi_ai/llm/__init__.py", "a", encoding="utf-8") as f:
    f.write("\nfrom .router import hybrid_router")

# ==========================================
# 4. ROOT CONFIG UPDATE
# ==========================================
root_toml = "pyproject.toml"
if os.path.exists(root_toml):
    with open(root_toml, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "multi-ai-schema" not in content:
        content = content.replace(
            'multi-ai-utils = {path = "./libs/utils", develop = true}',
            'multi-ai-utils = {path = "./libs/utils", develop = true}\nmulti-ai-schema = {path = "./libs/schema", develop = true}'
        )
        with open(root_toml, "w", encoding="utf-8") as f:
            f.write(content)
        print("? Added multi-ai-schema to root dependencies")

print("\n?? ALL V5.2 FILES INSTALLED SUCCESSFULLY!")
