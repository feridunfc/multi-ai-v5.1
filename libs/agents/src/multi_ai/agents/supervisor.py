from .base import BaseAgent

class EnhancedSupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Supervisor", model="qwen2.5:7b")
    
    async def review_process(self, context: dict):
        return "Approved"
