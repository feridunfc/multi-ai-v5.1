import logging
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)

@dataclass
class BudgetStats:
    total_tokens: int = 0
    total_cost: float = 0.0
    requests: int = 0

class BudgetGuard:
    PRICING = {
        'llama3.2:1b': 0.0,
        'gpt-4': 0.03,
        'gpt-3.5-turbo': 0.0015
    }

    def __init__(self, limit_usd: float = 10.0):
        self.limit = limit_usd
        self.stats = BudgetStats()

    def check_budget(self, estimated_cost: float) -> bool:
        # Backslash kaldirildi
        if (self.stats.total_cost + estimated_cost) > self.limit:
            logger.error(f'🛑 Budget Exceeded! Limit: {self.limit}, Used: {self.stats.total_cost}')
            return False
        return True

    def record_usage(self, provider: str, model: str, tokens: int):
        price = self.PRICING.get(model, 0.0)
        cost = (tokens / 1000) * price
        
        self.stats.total_tokens += tokens
        self.stats.total_cost += cost
        self.stats.requests += 1
        
        logger.info(f'💰 Cost:  | Total:  | Model: {model}')

budget_guard = BudgetGuard()
