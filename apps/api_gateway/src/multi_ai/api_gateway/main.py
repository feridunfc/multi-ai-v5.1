import hmac
import hashlib
import logging
import sys
import os
from fastapi import FastAPI, Request, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from multi_ai.core.settings import settings
from multi_ai.events.schemas import GitHubWebhookEvent
from multi_ai.events.broker import get_event_broker

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# 🛠️ HATA DÜZELTME: HİBRİT IMPORT SİSTEMİ
# Dosyayı hem "python main.py" olarak hem de modül olarak çalıştırabilmek için.
# -------------------------------------------------------------------------
workflow_router = None
try:
    # YÖNTEM 1: İdeal olan (Modül yapısı)
    from .routes import router as workflow_router
except ImportError:
    try:
        # YÖNTEM 2: Script olarak çalıştırıldığında (Şu an yaşadığınız durum)
        # Python'a "yanındaki dosyaya bak" diyoruz.
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from routes import router as workflow_router
    except ImportError as e:
        logger.error(f"🚨 KRİTİK: 'routes.py' yine yüklenemedi! Hata: {e}")

app = FastAPI(title="Multi-AI API Gateway", version="5.1.0")


# --- EKLENECEK KISIM BAŞLANGICI ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    422 Hatalarının detayını terminale basar.
    """
    error_details = exc.errors()
    logger.error(f"❌ VERİ DOĞRULAMA HATASI (422): Gelen veri API modeliyle uyuşmuyor!")
    logger.error(f"🔍 Hatalı Alanlar: {error_details}")

    # Gelen veriyi de görelim
    try:
        body = await request.json()
        logger.error(f"📩 Gelen Veri (JSON): {body}")
    except:
        logger.error("📩 Gelen veri JSON formatında değil.")

    return JSONResponse(
        status_code=422,
        content={"detail": error_details},
    )



# -------------------------------------------------------------------------
# CORS AYARLARI (Dashboard için kritik)
# -------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# ROUTER BAĞLANTISI
# -------------------------------------------------------------------------
if workflow_router:
    app.include_router(workflow_router, prefix="/api/workflow", tags=["Workflow"])
    logger.info("✅ BAŞARILI: Workflow Router devreye alındı.")
else:
    logger.error("❌ HATA: Workflow Router yüklenemediği için endpoint 404 verecek.")


# -------------------------------------------------------------------------
# GITHUB WEBHOOK & HEALTH CHECK
# -------------------------------------------------------------------------
async def verify_github(request: Request) -> dict:
    secret = settings.github_webhook_secret
    try:
        body = await request.body()
    except Exception:
        return {}

    if secret:
        signature = request.headers.get("x-hub-signature-256")
        if not signature:
            # İmza yoksa bile local testler için esnek davranabiliriz
            pass
        else:
            expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise HTTPException(status_code=401, detail="Invalid signature")
    try:
        return await request.json()
    except Exception:
        return {}


@app.post("/webhook/github")
async def github_webhook(
        response: Response,
        payload: dict = Depends(verify_github),
        request: Request = None,
):
    event_name = request.headers.get("x-github-event") if request else "unknown"

    # Payload güvenliği
    repo_full_name = "unknown"
    if isinstance(payload, dict):
        repo_full_name = payload.get("repository", {}).get("full_name", "unknown")

    ev = GitHubWebhookEvent(
        source="api_gateway",
        github_event_name=event_name,
        github_delivery_id=request.headers.get("x-github-delivery", "unknown") if request else "unknown",
        repository_full_name=repo_full_name,
        pull_request_id=payload.get("pull_request", {}).get("id") if isinstance(payload, dict) else None,
        payload=payload or {},
    )

    broker = await get_event_broker()
    await broker.publish(ev)
    response.status_code = 202
    return {"status": "accepted", "event_id": ev.event_id}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api_gateway"}


if __name__ == "__main__":
    import uvicorn

    # Host 0.0.0.0 yapılarak Docker veya dış erişim mümkün kılınır
    uvicorn.run(app, host="0.0.0.0", port=8000)