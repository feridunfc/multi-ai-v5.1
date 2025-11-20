import logging
import re
import os
from typing import Dict
from multi_ai.llm.hybrid_router import llm_router
from multi_ai.sandbox.filesystem import SandboxFileSystem
from multi_ai.rag.knowledge_base import rag_engine

logger = logging.getLogger(__name__)

class EnhancedCoderAgent:
    def __init__(self):
        self.llm = llm_router
        self.rag = rag_engine

    async def implement_artifact(self, artifact: Dict, task_id: str) -> str:
        # PATH CORRECTION: /home/user/... gibi yolları temizle, sadece dosya adını al
        raw_path = artifact.get('path', 'generated.py')
        filename = os.path.basename(raw_path) 
        
        logger.info(f"💻 Coder implementing: {filename}")
        
        # RAG ile ornek bul
        try:
            rag_results = self.rag.search(f"python code for {artifact.get('purpose')}", limit=1)
            ref_code = rag_results[0]['content'][:500] if rag_results else ""
        except:
            ref_code = ""

        prompt = f'''
        ROLE: Expert Python Developer
        FILE: {filename}
        PURPOSE: {artifact.get('purpose')}
        CONTEXT: {artifact.get('expected_behavior')}
        
        REFERENCE:
        {ref_code}
        
        TASK: Write the complete code for {filename}. 
        IMPORTANT: Return ONLY the code block wrapped in markdown like ```python ... ```
        '''
        
        try:
            response = await self.llm.complete(prompt=prompt, task_type="coding")
            
            code_match = re.search(r"\`\`\`(?:python)?(.*?)\`\`\`", response, re.DOTALL)
            code = code_match.group(1).strip() if code_match else response.strip()

            # Save to Sandbox (Artik guvenli filename kullaniyoruz)
            safe_id = task_id.replace('/', '_')
            fs = SandboxFileSystem(safe_id)
            file_path = fs.write_file(filename, code)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Coding failed: {e}")
            # Hata durumunda bos dosya yaz ki workflow devam etsin
            safe_id = task_id.replace('/', '_')
            fs = SandboxFileSystem(safe_id)
            return fs.write_file(filename, f"# Coding Error: {e}")
