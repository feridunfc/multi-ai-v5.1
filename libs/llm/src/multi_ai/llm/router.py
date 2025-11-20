import logging
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
