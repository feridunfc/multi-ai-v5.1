import logging
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from .metrics import BUDGET_USAGE

logger = logging.getLogger(__name__)


@dataclass
class BudgetStatus:
    daily_spent: float = 0.0
    daily_limit: float = 100.0
    monthly_spent: float = 0.0
    monthly_limit: float = 1000.0
    agent_breakdown: Dict[str, float] = field(default_factory=dict)


class BudgetGuard:
    PRICING = {
        'llama3.2:1b': 0.0,  # Local
        'gpt-4': 0.03,  # Cloud (High)
        'gpt-3.5-turbo': 0.0015  # Cloud (Low)
    }

    def __init__(self, daily_limit: float = 100.0):
        self.status = BudgetStatus(daily_limit=daily_limit)

    def check_budget(self, estimated_cost: float) -> bool:
        if (self.status.daily_spent + estimated_cost) > self.status.daily_limit:
            logger.error(f"🛑 Daily Budget Exceeded! Limit: ${self.status.daily_limit}")
            return False
        return True

    def record_usage(self, agent_id: str, model: str, tokens: int):
        cost = (tokens / 1000) * self.PRICING.get(model, 0.0)

        self.status.daily_spent += cost
        self.status.monthly_spent += cost

        current_agent_cost = self.status.agent_breakdown.get(agent_id, 0.0)
        self.status.agent_breakdown[agent_id] = current_agent_cost + cost

        # Prometheus Update
        BUDGET_USAGE.labels(agent_id=agent_id, model=model).inc(cost)

        logger.info(f"💰 Cost Recorded: ${cost:.6f} | Agent: {agent_id}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "spent": self.status.daily_spent,
            "limit": self.status.daily_limit,
            "monthly_spent": self.status.monthly_spent,
            "breakdown": self.status.agent_breakdown
        }


budget_guard = BudgetGuard()