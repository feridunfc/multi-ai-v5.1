import logging
import json
import re
from typing import Dict, Optional
from multi_ai.llm.client import llm_client

logger = logging.getLogger(__name__)

class EnhancedArchitectAgent:
    def __init__(self):
        self.llm = llm_client

    async def create_manifest(self, research: dict, goal: str) -> Dict:
        logger.info(f'🏗️ Architect designing manifest for: {goal}')
        
        prompt = f'''
        ROLE: Architect. GOAL: {goal}.
        OUTPUT: JSON with artifacts list (path, purpose).
        '''
        
        try:
            response = await self.llm.generate(prompt=prompt)
            # Temizleme
            clean = re.sub(r'`(?:\w+)?\s*', '', response).replace('`', '').strip()
            # Bazen LLM sadece aciklama yazar, JSON bulmaya calisalim
            json_match = re.search(r'\{.*\}', clean, re.DOTALL)
            if json_match:
                clean = json_match.group(0)
            
            data = json.loads(clean)
            if 'artifacts' not in data: 
                raise ValueError('Missing artifacts key')
            return data
            
        except Exception as e:
            logger.warning(f'Architect JSON fail: {e}. Using Fallback.')
            # Fallback Plan (Yedek)
            return {
                'sprint_id': 'fallback_sprint', 
                'artifacts': [
                    {
                        'path': 'main.py', 
                        'purpose': f'Implement {goal}', 
                        'type': 'code',
                        'expected_behavior': f'Logic for {goal}'
                    }
                ]
            }
