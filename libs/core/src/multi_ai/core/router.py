import logging
from typing import Dict, Any
# Burasi normalde cloud clientlari import eder ama MVP icin mockluyoruz
from .settings import settings

logger = logging.getLogger(__name__)

class HybridRouter:
    def __init__(self):
        self.local_model = 'llama3.2:1b'
        self.cloud_model = 'gpt-4-turbo'

    def route(self, prompt: str, task_complexity: str = 'medium') -> dict:
        # Basit mantik: Kod yazma ve Karmasik isler -> Cloud (Simule), Digerleri -> Local
        # Not: Senin sisteminde API Key olmadigi icin simdilik hep LOCAL zorluyoruz.
        
        decision = {
            'provider': 'ollama',
            'model': self.local_model,
            'reason': 'Local preference / No API Key'
        }
        
        if task_complexity == 'high' and settings.openai_api_key:
             decision = {
                'provider': 'openai',
                'model': self.cloud_model,
                'reason': 'High complexity task'
            }
            
        logger.info(f"Routing Decision: {decision['provider']} ({decision['reason']})")
        return decision

hybrid_router = HybridRouter()
