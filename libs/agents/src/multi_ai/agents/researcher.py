import logging
import json
from typing import Dict, Optional
from datetime import datetime
from multi_ai.llm.hybrid_router import llm_router
from multi_ai.rag.knowledge_base import rag_engine

logger = logging.getLogger(__name__)

class EnhancedResearcherAgent:
    def __init__(self):
        self.llm = llm_router
        self.rag = rag_engine

    async def conduct_research(self, goal: str, context: Optional[Dict] = None) -> Dict:
        context = context or {}
        logger.info(f"🔎 Researcher starting (RAG Enhanced): {goal}")

        # 1. HAFIZAYI TARA
        logger.info("🧠 Scanning codebase for context...")
        try:
            rag_results = self.rag.search(goal, limit=3)
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")
            rag_results = []
        
        # Bulunan dosyalardan özet çıkar
        context_str = ""
        found_files = []
        for r in rag_results:
            path = r.get("path", "unknown")
            score = r.get("score", 0)
            # Dosya yolunu kısaltalım
            short_path = path.split("multi_ai")[-1] if "multi_ai" in path else path
            found_files.append(short_path)
            
            content = r.get("content", "")
            context_str += f"\n--- FILE: {short_path} (Relevance: {score:.2f}) ---\n"
            context_str += content[:1500] + "...\n"

        logger.info(f"🧠 Found relevant context in: {found_files}")

        # 2. PROMPT HAZIRLA
        prompt = f'''
        ROLE: Senior Tech Researcher
        GOAL: {goal}
        
        EXISTING CODEBASE CONTEXT (Use this to maintain consistency):
        {context_str}
        
        TASK: Analyze requirements. If existing code matches, recommend reuse.
        OUTPUT: JSON with keys (analysis, tech_stack, existing_components_found, feasibility).
        '''
        
        try:
            response = await self.llm.complete(prompt=prompt, task_type="research", json_mode=True)
            
            # Temizleme
            clean_json = response.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(clean_json)
            except:
                # LLM bazen duz metin donerse
                data = {"analysis": response, "tech_stack": [], "existing_components_found": found_files}
            
            data["metadata"] = {
                "rag_sources": found_files,
                "timestamp": datetime.now().isoformat()
            }
            return data
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {"error": str(e), "status": "failed"}
