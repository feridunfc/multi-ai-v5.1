import logging
import json
from typing import Dict, Optional
from datetime import datetime
from multi_ai.llm.client import llm_client

logger = logging.getLogger(__name__)

class EnhancedResearcherAgent:
    def __init__(self):
        self.llm = llm_client

    async def conduct_research(self, goal: str, context: Optional[Dict] = None) -> Dict:
        context = context or {}
        logger.info(f'🔎 Researcher starting: {goal}')

        prompt = f'''
        ROLE: Senior Tech Researcher
        GOAL: {goal}
        CONTEXT: {json.dumps(context)}
        
        TASK: Analyze requirements, tech stack, and risks.
        OUTPUT: JSON with keys (tech_stack, architecture, risks, feasibility).
        '''
        
        try:
            response = await self.llm.generate(prompt=prompt, system_prompt='You are a Researcher.')
            # JSON temizleme (Basit)
            clean_json = response.replace('`json', '').replace('`', '').strip()
            data = json.loads(clean_json)
            
            # Metadata ekle
            data['metadata'] = {
                'research_id': f'res_{int(datetime.now().timestamp())}',
                'timestamp': datetime.now().isoformat()
            }
            return data
        except Exception as e:
            logger.error(f'Research failed: {e}')
            return {'error': str(e), 'status': 'failed'}
