import logging
import json
from typing import Dict, Optional
from multi_ai.llm.client import llm_client

logger = logging.getLogger(__name__)

class EnhancedSupervisorAgent:
    def __init__(self):
        self.llm = llm_client

    async def supervise_sprint(self, sprint_data: Dict) -> Dict:
        logger.info('👀 Supervisor reviewing sprint...')
        
        prompt = f'''
        ROLE: Project Supervisor & QA Lead
        DATA: {json.dumps(sprint_data)}
        
        TASK: Evaluate quality, risks and approve/reject.
        OUTPUT: JSON {{ "decision": "approved|rejected", "score": 0-100, "reason": "..." }}
        '''
        
        try:
            response = await self.llm.generate(prompt=prompt)
            clean_json = response.replace('`json', '').replace('`', '').strip()
            return json.loads(clean_json)
        except Exception as e:
            return {'decision': 'rejected', 'reason': f'Supervision failed: {e}'}
