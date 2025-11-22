import asyncio
import logging
import sys
import os


# --- CRITICAL FIX: EN BAŞTA YOLLARI AYARLA ---
def setup_paths():
    """Proje yollarını doğru şekilde ayarlar - AGGRESSIVE FIX"""
    # Proje Kök Dizinini Belirle
    # __file__ kullanarak dinamik bulmak daha güvenlidir ama manuel de olur
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # apps/review_worker/src/multi_ai/review_worker -> ../../../../.. -> Root
    project_root = os.path.abspath(os.path.join(current_dir, "../../../../../"))

    # Eğer otomatik bulamazsa manuel yolu kullan (Yedek)
    if not os.path.exists(os.path.join(project_root, "libs")):
        project_root = r"C:\Users\user\PycharmProjects\MULTI_AI_v51"

    print(f"🎯 Proje Kök Dizini: {project_root}")

    # Eklenecek kritik yollar
    paths_to_add = [
        os.path.join(project_root, "libs", "utils", "src"),
        os.path.join(project_root, "libs", "agents", "src"),
        os.path.join(project_root, "libs", "orchestrator", "src"),
        os.path.join(project_root, "libs", "core", "src"),
        os.path.join(project_root, "libs", "llm", "src"),
        os.path.join(project_root, "libs", "rag", "src"),
        os.path.join(project_root, "libs", "compliance", "src"),
        os.path.join(project_root, "libs", "sandbox", "src"),
        os.path.join(project_root, "libs", "git", "src"),
        project_root  # Root'u da ekle
    ]

    # Yolları sys.path'in en başına ekle
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)
            print(f"✅ Yol Eklendi: {p}")


setup_paths()  # <--- KRİTİK: Bunu en başta çağırıyoruz

# --- ŞİMDİ IMPORTLARI YAPABİLİRİZ ---
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from multi_ai.core.settings import settings
from multi_ai.orchestrator.workflows import SupervisorWorkflow
from multi_ai.orchestrator.activities import AgentActivities
from multi_ai.utils.robust_ollama_client import RobustOllamaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🚀 Worker Başlatılıyor...")

    # 1. Ollama Bağlantı Testi
    logger.info(f"🔌 Ollama Bağlantısı Test Ediliyor ({settings.ollama.base_url})...")
    try:
        client = RobustOllamaClient()
        # Basit bir ping at
        await client.generate(model="llama3.2:1b", prompt="ping", options={"num_ctx": 1})
        logger.info("✅ Ollama Bağlantısı BAŞARILI!")
    except Exception as e:
        logger.error(f"❌ Ollama Bağlantı Hatası: {e}")
        logger.warning("⚠️ Devam ediliyor ama ajanlar hata verebilir...")

    # 2. Temporal Bağlantısı
    logger.info(f"🔌 Temporal'a bağlanılıyor ({settings.temporal.address})...")
    try:
        client = await Client.connect(settings.temporal.address, namespace="default")
    except Exception as e:
        logger.error(f"❌ Temporal Bağlantı Hatası: {e}")
        return

    # 3. Worker Yapılandırması
    activities = AgentActivities()

    runner = SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules(
            "multi_ai", "pydantic", "pydantic_settings", "pathlib", "os",
            "logging", "git", "sqlite3", "cryptography", "json", "subprocess", "sys", "httpx", "tenacity"
        )
    )

    worker = Worker(
        client,
        task_queue=settings.temporal.task_queue,
        workflows=[SupervisorWorkflow],
        activities=[
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
    logger.info("waiting for tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())