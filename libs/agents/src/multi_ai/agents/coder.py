import logging
import re
from typing import Dict
from multi_ai.llm.client import llm_client
from multi_ai.sandbox.filesystem import SandboxFileSystem

logger = logging.getLogger(__name__)

class EnhancedCoderAgent:
    def __init__(self):
        self.llm = llm_client

    async def implement_artifact(self, artifact: Dict, task_id: str) -> str:
        logger.info(f"💻 Coder implementing: {artifact.get('path')}")
        
        prompt = f'''
        ROLE: Expert Developer
        FILE: {artifact.get('path')}
        PURPOSE: {artifact.get('purpose')}
        CONTEXT: {artifact.get('expected_behavior')}
        
        TASK: Write the complete code for this file. Return ONLY code.
        '''
        
        try:
            response = await self.llm.generate(prompt=prompt)
            
            # Code cleaning
            code = re.sub(r'`(?:\w+)?\s*', '', response).replace('`', '').strip()
            
            # Save to Sandbox
            safe_id = task_id.replace('/', '_')
            fs = SandboxFileSystem(safe_id)
            path = fs.write_file(artifact['path'], code)
            
            return path
        except Exception as e:
            logger.error(f'Coding failed: {e}')
            raise e
