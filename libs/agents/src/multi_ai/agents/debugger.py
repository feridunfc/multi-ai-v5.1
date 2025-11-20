import logging
from typing import Dict
from multi_ai.llm.hybrid_router import llm_router

logger = logging.getLogger(__name__)

class EnhancedDebuggerAgent:
    def __init__(self):
        self.llm = llm_router

    async def diagnose_error(self, code_context: str, error_log: str) -> Dict:
        logger.info("🚑 Debugger diagnosing error...")
        
        prompt = f'''
        ROLE: Senior Python Debugger
        TASK: Fix the code based on the error log.
        
        BROKEN CODE:
        {code_context}
        
        ERROR LOG:
        {error_log}
        
        INSTRUCTION: Analyze the error and provide the FIXED code.
        Return ONLY the fixed code block.
        '''
        
        try:
            response = await self.llm.complete(prompt=prompt, task_type="coding")
            return {"diagnosis": "Fix applied", "fixed_code": response}
        except Exception as e:
            logger.error(f"Debugger failed: {e}")
            return {"error": str(e)}
