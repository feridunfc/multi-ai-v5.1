import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Bagimliliklar
from multi_ai.core.budget import budget_guard
from multi_ai.utils.robust_ollama_client import RobustOllamaClient

logger = logging.getLogger(__name__)

@dataclass
class RoutingDecision:
    use_cloud: bool
    provider: str
    model: str
    reason: str
    estimated_cost: float

class HybridIntelligenceRouter:
    def __init__(self) -> None:
        self.budget_guard = budget_guard
        self.local_client = RobustOllamaClient()
        # Cloud clientlar ilerde eklenebilir
        
    async def complete(self, prompt: str, json_mode: bool = False, **kwargs) -> str:
        # Karar Mekanizmasi
        task_type = kwargs.get("task_type", "general")
        decision = self._make_routing_decision(task_type, prompt)
        
        logger.info(f"🧠 Router: {decision.provider}/{decision.model} ({decision.reason})")

        # Butce Kontrol
        if decision.use_cloud:
            if not self.budget_guard.check_budget(decision.estimated_cost):
                logger.warning("Budget exceeded! Fallback to LOCAL.")
                decision = RoutingDecision(False, "ollama", "llama3.2:1b", "Budget Fallback", 0.0)

        # Yurutme
        try:
            # Simdilik sadece Local calistiriyoruz (API Key yoksa)
            return await self._call_local(decision.model, prompt)
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return await self._call_local("llama3.2:1b", prompt)

    def _make_routing_decision(self, task_type: str, prompt: str) -> RoutingDecision:
        # Basit kural seti
        complexity = "high" if len(prompt) > 1000 or "architect" in task_type else "low"
        
        # Eger OpenAI API key varsa ve is zorsa Cloud kullan (Simdilik kapali)
        # if complexity == "high" and os.getenv("OPENAI_API_KEY"):
        #     return RoutingDecision(True, "openai", "gpt-4-turbo", "High Complexity", 0.03)
        
        return RoutingDecision(False, "ollama", "llama3.2:1b", "Local Preference", 0.0)

    async def _call_local(self, model: str, prompt: str) -> str:
        resp = await self.local_client.generate(model, prompt)
        # Istatistik kaydet
        self.budget_guard.record_usage("local", model, len(prompt)/4)
        return resp.content

llm_router = HybridIntelligenceRouter()
