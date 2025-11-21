import logging
import uuid
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from temporalio.client import Client

# AYARLARI IMPORT ET
from multi_ai.core.settings import settings

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# --- VERİ MODELİ ---
class WorkflowRequest(BaseModel):
    repo_url: str = "https://github.com/feridunfc/multi-ai-v5.1"
    branch: str = "main"
    prompt: Optional[str] = None
    task_description: Optional[str] = None
    priority: str = "Orta"
    source: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# --- TEMPORAL BAĞLANTISI VE TETİKLEME ---
@router.post("/trigger")
async def trigger_workflow(request: WorkflowRequest):
    """
    Dashboard'dan gelen görevi Temporal İş Akışına iletir.
    """
    final_prompt = request.task_description or request.prompt or "Boş Görev"
    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"

    target_queue = settings.temporal.task_queue
    logger.info(f"🔌 Temporal'a bağlanılıyor... Hedef Kuyruk: '{target_queue}'")

    try:
        # 1. Temporal Sunucusuna Bağlan
        client = await Client.connect("localhost:7233")

        # 2. Workflow İçin Girdi Verisini Hazırla (Dictionary)
        workflow_input = {
            "task_description": final_prompt,
            "priority": request.priority,
            "repo_url": request.repo_url,
            "branch": request.branch
        }

        # 3. İş Akışını Başlat
        handle = await client.start_workflow(
            "SupervisorWorkflow",
            args=[workflow_input],  # TEK DOĞRU FORMAT BUDUR: [dict]
            id=workflow_id,
            task_queue=target_queue,
        )

        logger.info(f"🚀 [TEMPORAL] İş Akışı Başlatıldı! Run ID: {handle.run_id}")

        return {
            "status": "started",
            "workflow_id": workflow_id,
            "run_id": handle.run_id,
            "queue": target_queue,
            "message": f"Görev '{target_queue}' kuyruğuna iletildi."
        }

    except Exception as e:
        logger.error(f"❌ Temporal Bağlantı Hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow başlatılamadı: {str(e)}")