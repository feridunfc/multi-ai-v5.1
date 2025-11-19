import hmac
import hashlib
import logging
from fastapi import FastAPI, Request, HTTPException, Response, Depends

from multi_ai.core.settings import settings
from multi_ai.events.schemas import GitHubWebhookEvent
from multi_ai.events.broker import get_event_broker

logger = logging.getLogger(__name__)
app = FastAPI(title="Multi-AI API Gateway", version="5.1.0")


async def verify_github(request: Request) -> dict:
    secret = settings.github_webhook_secret
    body = await request.body()

    # Optional: Only verify if secret is set
    if secret:
        signature = request.headers.get("x-hub-signature-256")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing signature")
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
    event_name = request.headers.get("x-github-event") if request else None
    delivery_id = request.headers.get("x-github-delivery") if request else None

    ev = GitHubWebhookEvent(
        source="api_gateway",
        github_event_name=event_name or "unknown",
        github_delivery_id=delivery_id or "unknown",
        repository_full_name=payload.get("repository", {}).get("full_name", "unknown"),
        pull_request_id=payload.get("pull_request", {}).get("id"),
        commit_sha=payload.get("head_commit", {}).get("id"),
        payload=payload,
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
