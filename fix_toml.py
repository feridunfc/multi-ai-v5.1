# # # # # # # # import os
# # # # # # # # from pathlib import Path
# # # # # # # #
# # # # # # # # # --- 1. DOSYA İÇERİKLERİ (Doğru Bağımlılık Ağacı ile) ---
# # # # # # # #
# # # # # # # # ROOT_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-workspace"
# # # # # # # # version = "5.1.0"
# # # # # # # # description = "Multi-AI Enterprise Monorepo Root"
# # # # # # # # authors = ["Feridun <email@address.com>"]
# # # # # # # # package-mode = false
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # #
# # # # # # # # # Local Libraries
# # # # # # # # multi-ai-core = {path = "./libs/core", develop = true}
# # # # # # # # multi-ai-utils = {path = "./libs/utils", develop = true}
# # # # # # # # multi-ai-llm = {path = "./libs/llm", develop = true}
# # # # # # # # multi-ai-rag = {path = "./libs/rag", develop = true}
# # # # # # # # multi-ai-agents = {path = "./libs/agents", develop = true}
# # # # # # # # multi-ai-orchestrator = {path = "./libs/orchestrator", develop = true}
# # # # # # # #
# # # # # # # # # External Dependencies
# # # # # # # # streamlit = "^1.32.0"
# # # # # # # # plotly = "^5.19.0"
# # # # # # # # fastapi = "^0.109.0"
# # # # # # # # uvicorn = "^0.27.0"
# # # # # # # # temporalio = "^1.4.0"
# # # # # # # # matplotlib = "^3.8.0"
# # # # # # # # Pillow = "^10.0.0"
# # # # # # # # watchdog = "^4.0.0"
# # # # # # # # scipy = "^1.11.0"
# # # # # # # # requests = "^2.31.0"
# # # # # # # # httpx = "^0.27.0"
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # CORE_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-core"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "Core System Config"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # pydantic = "^2.6.0"
# # # # # # # # pydantic-settings = "^2.2.0"
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # UTILS_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-utils"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "Shared Utilities"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # httpx = "^0.27.0"
# # # # # # # # requests = "^2.31.0"
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # LLM_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-llm"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "LLM Client"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # # # multi-ai-utils = {path = "../utils", develop = true}
# # # # # # # # openai = "^1.12.0"
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # RAG_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-rag"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "RAG System"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # # # multi-ai-utils = {path = "../utils", develop = true}
# # # # # # # # multi-ai-llm = {path = "../llm", develop = true}
# # # # # # # # qdrant-client = "^1.7.0"
# # # # # # # # sentence-transformers = "^2.2.2"
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # AGENTS_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-agents"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "AI Agents"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # # # multi-ai-utils = {path = "../utils", develop = true}
# # # # # # # # multi-ai-llm = {path = "../llm", develop = true}
# # # # # # # # multi-ai-rag = {path = "../rag", develop = true}
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # ORCH_TOML = """[tool.poetry]
# # # # # # # # name = "multi-ai-orchestrator"
# # # # # # # # version = "0.1.0"
# # # # # # # # description = "Workflow Orchestrator"
# # # # # # # # authors = ["MultiAI Team"]
# # # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # # #
# # # # # # # # [tool.poetry.dependencies]
# # # # # # # # python = "^3.10"
# # # # # # # # temporalio = "^1.4.0"
# # # # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # # # multi-ai-agents = {path = "../agents", develop = true}
# # # # # # # #
# # # # # # # # [build-system]
# # # # # # # # requires = ["poetry-core"]
# # # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # # """
# # # # # # # #
# # # # # # # # # --- 2. DOSYA YAZMA İŞLEMİ ---
# # # # # # # #
# # # # # # # # FILES = {
# # # # # # # #     "pyproject.toml": ROOT_TOML,
# # # # # # # #     "libs/core/pyproject.toml": CORE_TOML,
# # # # # # # #     "libs/utils/pyproject.toml": UTILS_TOML,
# # # # # # # #     "libs/llm/pyproject.toml": LLM_TOML,
# # # # # # # #     "libs/rag/pyproject.toml": RAG_TOML,
# # # # # # # #     "libs/agents/pyproject.toml": AGENTS_TOML,
# # # # # # # #     "libs/orchestrator/pyproject.toml": ORCH_TOML,
# # # # # # # # }
# # # # # # # #
# # # # # # # #
# # # # # # # # def main():
# # # # # # # #     print("🚀 TOML Dosyaları Onarılıyor...")
# # # # # # # #
# # # # # # # #     for path_str, content in FILES.items():
# # # # # # # #         path = Path(path_str)
# # # # # # # #
# # # # # # # #         # Klasör yoksa oluştur
# # # # # # # #         if not path.parent.exists():
# # # # # # # #             path.parent.mkdir(parents=True, exist_ok=True)
# # # # # # # #             print(f"📁 Klasör oluşturuldu: {path.parent}")
# # # # # # # #
# # # # # # # #         # Varsa sil (Bozuk encoding'den kurtulmak için)
# # # # # # # #         if path.exists():
# # # # # # # #             os.remove(path)
# # # # # # # #
# # # # # # # #         # Temiz UTF-8 olarak yaz
# # # # # # # #         with open(path, "w", encoding="utf-8", newline="\n") as f:
# # # # # # # #             f.write(content.strip() + "\n")
# # # # # # # #
# # # # # # # #         print(f"✅ Güncellendi: {path}")
# # # # # # # #
# # # # # # # #     print("\n✨ İşlem Tamamlandı! Şimdi 'poetry install' çalıştırabilirsiniz.")
# # # # # # # #
# # # # # # # #
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     main()
# # # # # # #
# # # # # # # import os
# # # # # # #
# # # # # # # # Doğru TOML içeriği
# # # # # # # content = """[tool.poetry]
# # # # # # # name = "multi-ai-events"
# # # # # # # version = "0.1.0"
# # # # # # # description = "Event Schemas"
# # # # # # # authors = ["MultiAI Team"]
# # # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # # #
# # # # # # # [tool.poetry.dependencies]
# # # # # # # python = "^3.10"
# # # # # # # pydantic = "^2.6.0"
# # # # # # #
# # # # # # # [build-system]
# # # # # # # requires = ["poetry-core"]
# # # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # # """
# # # # # # #
# # # # # # # file_path = "libs/events/pyproject.toml"
# # # # # # #
# # # # # # # # Klasör yoksa oluştur
# # # # # # # os.makedirs(os.path.dirname(file_path), exist_ok=True)
# # # # # # #
# # # # # # # # Dosyayı temiz UTF-8 olarak yaz
# # # # # # # with open(file_path, "w", encoding="utf-8", newline="\n") as f:
# # # # # # #     f.write(content.strip() + "\n")
# # # # # # #
# # # # # # # print(f"✅ {file_path} başarıyla onarıldı!")
# # # # # #
# # # # # # import os
# # # # # # from pathlib import Path
# # # # # #
# # # # # # # --- 1. EKSİK MODÜLLERİN TOML İÇERİKLERİ ---
# # # # # #
# # # # # # SANDBOX_TOML = """[tool.poetry]
# # # # # # name = "multi-ai-sandbox"
# # # # # # version = "0.1.0"
# # # # # # description = "Secure Code Execution Environment"
# # # # # # authors = ["MultiAI Team"]
# # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # #
# # # # # # [tool.poetry.dependencies]
# # # # # # python = "^3.10"
# # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # multi-ai-utils = {path = "../utils", develop = true}
# # # # # #
# # # # # # [build-system]
# # # # # # requires = ["poetry-core"]
# # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # """
# # # # # #
# # # # # # COMPLIANCE_TOML = """[tool.poetry]
# # # # # # name = "multi-ai-compliance"
# # # # # # version = "0.1.0"
# # # # # # description = "Security & Compliance Checks"
# # # # # # authors = ["MultiAI Team"]
# # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # #
# # # # # # [tool.poetry.dependencies]
# # # # # # python = "^3.10"
# # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # multi-ai-llm = {path = "../llm", develop = true}
# # # # # #
# # # # # # [build-system]
# # # # # # requires = ["poetry-core"]
# # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # """
# # # # # #
# # # # # # GIT_TOML = """[tool.poetry]
# # # # # # name = "multi-ai-git"
# # # # # # version = "0.1.0"
# # # # # # description = "Git Operations Manager"
# # # # # # authors = ["MultiAI Team"]
# # # # # # packages = [{include = "multi_ai", from = "src"}]
# # # # # #
# # # # # # [tool.poetry.dependencies]
# # # # # # python = "^3.10"
# # # # # # multi-ai-core = {path = "../core", develop = true}
# # # # # # multi-ai-utils = {path = "../utils", develop = true}
# # # # # #
# # # # # # [build-system]
# # # # # # requires = ["poetry-core"]
# # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # """
# # # # # #
# # # # # # # --- 2. GÜNCELLENMİŞ ROOT TOML (HEPSİNİ İÇERİR) ---
# # # # # #
# # # # # # ROOT_TOML = """[tool.poetry]
# # # # # # name = "multi-ai-workspace"
# # # # # # version = "5.2.0"
# # # # # # description = "Multi-AI Enterprise Monorepo Root"
# # # # # # authors = ["Feridun <email@address.com>"]
# # # # # # package-mode = false
# # # # # #
# # # # # # [tool.poetry.dependencies]
# # # # # # python = "^3.10"
# # # # # #
# # # # # # # --- LOCAL LIBRARIES (TAM LİSTE) ---
# # # # # # multi-ai-core = {path = "./libs/core", develop = true}
# # # # # # multi-ai-utils = {path = "./libs/utils", develop = true}
# # # # # # multi-ai-llm = {path = "./libs/llm", develop = true}
# # # # # # multi-ai-rag = {path = "./libs/rag", develop = true}
# # # # # # multi-ai-agents = {path = "./libs/agents", develop = true}
# # # # # # multi-ai-orchestrator = {path = "./libs/orchestrator", develop = true}
# # # # # # multi-ai-events = {path = "./libs/events", develop = true}
# # # # # # # Yeni eklenenler:
# # # # # # multi-ai-sandbox = {path = "./libs/sandbox", develop = true}
# # # # # # multi-ai-compliance = {path = "./libs/compliance", develop = true}
# # # # # # multi-ai-git = {path = "./libs/git", develop = true}
# # # # # #
# # # # # # # --- EXTERNAL DEPENDENCIES ---
# # # # # # streamlit = "^1.32.0"
# # # # # # plotly = "^5.19.0"
# # # # # # fastapi = "^0.109.0"
# # # # # # uvicorn = "^0.27.0"
# # # # # # temporalio = "^1.4.0"
# # # # # # matplotlib = "^3.8.0"
# # # # # # Pillow = "^10.0.0"
# # # # # # watchdog = "^4.0.0"
# # # # # # scipy = "^1.11.0"
# # # # # # requests = "^2.31.0"
# # # # # # httpx = "^0.27.0"
# # # # # # faststream = "^0.4.0"
# # # # # # # Tırnak içinde yazılması gereken özel paketler
# # # # # # "faststream[redis]" = "^0.4.0"
# # # # # # cryptography = "^42.0.0"
# # # # # # prometheus-client = "^0.20.0"
# # # # # #
# # # # # # [build-system]
# # # # # # requires = ["poetry-core"]
# # # # # # build-backend = "poetry.core.masonry.api"
# # # # # # """
# # # # # #
# # # # # # # --- 3. DOSYA YAZMA ---
# # # # # #
# # # # # # FILES = {
# # # # # #     "libs/sandbox/pyproject.toml": SANDBOX_TOML,
# # # # # #     "libs/compliance/pyproject.toml": COMPLIANCE_TOML,
# # # # # #     "libs/git/pyproject.toml": GIT_TOML,
# # # # # #     "pyproject.toml": ROOT_TOML
# # # # # # }
# # # # # #
# # # # # #
# # # # # # def main():
# # # # # #     print("🚀 Eksik Modüller Onarılıyor...")
# # # # # #
# # # # # #     for path_str, content in FILES.items():
# # # # # #         path = Path(path_str)
# # # # # #
# # # # # #         # Klasör yoksa oluştur
# # # # # #         if not path.parent.exists():
# # # # # #             path.parent.mkdir(parents=True, exist_ok=True)
# # # # # #             print(f"📁 Klasör oluşturuldu: {path.parent}")
# # # # # #
# # # # # #         # Dosyayı yaz (UTF-8)
# # # # # #         with open(path, "w", encoding="utf-8", newline="\n") as f:
# # # # # #             f.write(content.strip() + "\n")
# # # # # #
# # # # # #         print(f"✅ Güncellendi: {path}")
# # # # # #
# # # # # #     print("\n✨ İşlem Tamamlandı! Lütfen 'poetry install' çalıştırın.")
# # # # # #
# # # # # #
# # # # # # if __name__ == "__main__":
# # # # # #     main()
# # # # #
# # # # # import os
# # # # #
# # # # # # Doğru ve Güncel Bağımlılıklar
# # # # # ROOT_TOML = """[tool.poetry]
# # # # # name = "multi-ai-workspace"
# # # # # version = "5.2.0"
# # # # # description = "Multi-AI Enterprise Monorepo Root"
# # # # # authors = ["Feridun <email@address.com>"]
# # # # # package-mode = false
# # # # #
# # # # # [tool.poetry.dependencies]
# # # # # python = "^3.10"
# # # # #
# # # # # # --- LOCAL LIBRARIES ---
# # # # # multi-ai-core = {path = "./libs/core", develop = true}
# # # # # multi-ai-utils = {path = "./libs/utils", develop = true}
# # # # # multi-ai-llm = {path = "./libs/llm", develop = true}
# # # # # multi-ai-rag = {path = "./libs/rag", develop = true}
# # # # # multi-ai-agents = {path = "./libs/agents", develop = true}
# # # # # multi-ai-orchestrator = {path = "./libs/orchestrator", develop = true}
# # # # # multi-ai-events = {path = "./libs/events", develop = true}
# # # # # multi-ai-sandbox = {path = "./libs/sandbox", develop = true}
# # # # # multi-ai-compliance = {path = "./libs/compliance", develop = true}
# # # # # multi-ai-git = {path = "./libs/git", develop = true}
# # # # #
# # # # # # --- EXTERNAL DEPENDENCIES ---
# # # # # streamlit = "^1.32.0"
# # # # # plotly = "^5.19.0"
# # # # # fastapi = "^0.109.0"
# # # # # uvicorn = "^0.27.0"
# # # # # temporalio = "^1.4.0"
# # # # # matplotlib = "^3.8.0"
# # # # # Pillow = "^10.0.0"
# # # # # watchdog = "^4.0.0"
# # # # # scipy = "^1.11.0"
# # # # # requests = "^2.31.0"
# # # # # httpx = "^0.27.0"
# # # # # cryptography = "^42.0.0"
# # # # # prometheus-client = "^0.20.0"
# # # # #
# # # # # # FastStream'i doğru şekilde (Extras ile) ekliyoruz
# # # # # faststream = {extras = ["redis"], version = "^0.5.0"}
# # # # #
# # # # # [build-system]
# # # # # requires = ["poetry-core"]
# # # # # build-backend = "poetry.core.masonry.api"
# # # # # """
# # # # #
# # # # # file_path = "pyproject.toml"
# # # # #
# # # # # with open(file_path, "w", encoding="utf-8", newline="\n") as f:
# # # # #     f.write(ROOT_TOML.strip() + "\n")
# # # # #
# # # # # print(f"✅ {file_path} bağımlılıkları düzeltildi!")
# # # #
# # # #
# # # # import os
# # # #
# # # # # --- 1. RESEARCHER AGENT (Düzeltilmiş) ---
# # # # researcher_code = """import logging
# # # # from typing import Dict, Any, List
# # # # from .base import BaseAgent
# # # #
# # # # logger = logging.getLogger(__name__)
# # # #
# # # # class EnhancedResearcherAgent(BaseAgent):
# # # #     def __init__(self):
# # # #         super().__init__(role="Researcher", model="llama3.2:3b")
# # # #
# # # #     async def conduct_research(self, query: str) -> Dict[str, Any]:
# # # #         system_prompt = \"\"\"
# # # #         SEN KIDEMLİ BİR TEKNİK ARAŞTIRMACISIN (SENIOR TECHNICAL RESEARCHER).
# # # #         Görevin: Verilen yazılım görevini analiz etmek ve GÜNCEL, DOĞRU teknik bilgiler sağlamaktır.
# # # #
# # # #         KURALLAR:
# # # #         1. ASLA hayali kütüphane veya modül uydurma. Sadece 'requests', 'pandas', 'numpy' gibi standart ve kanıtlanmış kütüphaneleri öner.
# # # #         2. Eğer emin değilsen "Bilmiyorum" de, uydurma.
# # # #         3. Kodun çalışacağı ortamı (Python 3.10+) göz önünde bulundur.
# # # #         4. Çıktın sadece teknik gerçekleri içermeli, laf kalabalığı yapma.
# # # #         \"\"\"
# # # #
# # # #         logger.info(f"🔎 Araştırma yapılıyor: {query}")
# # # #         result = await self._ask_llm(system_prompt, query)
# # # #
# # # #         return {
# # # #             "query": query,
# # # #             "findings": result,
# # # #             "source": "Local Knowledge & RAG"
# # # #         }
# # # # """
# # # #
# # # # # --- 2. ARCHITECT AGENT (Düzeltilmiş) ---
# # # # architect_code = """import logging
# # # # import json
# # # # from typing import Dict, Any, List
# # # # from .base import BaseAgent
# # # #
# # # # logger = logging.getLogger(__name__)
# # # #
# # # # class EnhancedArchitectAgent(BaseAgent):
# # # #     def __init__(self):
# # # #         super().__init__(role="Architect", model="qwen2.5:7b")
# # # #
# # # #     async def create_manifest(self, research_data: dict, task: str) -> Dict[str, Any]:
# # # #         system_prompt = \"\"\"
# # # #         SEN BAŞ YAZILIM MİMARISIN (CHIEF SOFTWARE ARCHITECT).
# # # #         Görevin: Verilen görevi, hatasız çalışacak bir dosya yapısına ve uygulama planına dönüştürmektir.
# # # #
# # # #         ÇIKTI FORMATI (KESİNLİKLE JSON):
# # # #         {
# # # #             "project_name": "proje_adi",
# # # #             "description": "Proje açıklaması",
# # # #             "dependencies": ["flask", "requests"],
# # # #             "artifacts": [
# # # #                 {
# # # #                     "path": "main.py",
# # # #                     "purpose": "Ana uygulama mantığı",
# # # #                     "instructions": "Detaylı talimatlar..."
# # # #                 }
# # # #             ]
# # # #         }
# # # #
# # # #         KURALLAR:
# # # #         1. Sadece geçerli JSON döndür. Başka hiçbir metin yazma.
# # # #         2. Dosya yolları mantıklı ve düzenli olsun.
# # # #         3. 'dependencies' listesine sadece gerçekten gerekenleri ekle.
# # # #         \"\"\"
# # # #
# # # #         context = f"Task: {task}\\nResearch: {json.dumps(research_data)}"
# # # #         logger.info(f"🏗️ Mimari plan hazırlanıyor...")
# # # #
# # # #         raw_response = await self._ask_llm(system_prompt, context, json_mode=True)
# # # #
# # # #         try:
# # # #             return json.loads(raw_response)
# # # #         except json.JSONDecodeError:
# # # #             logger.error("Architect JSON üretemedi, Fallback kullanılıyor.")
# # # #             return {
# # # #                 "project_name": "fallback_project",
# # # #                 "artifacts": [{"path": "main.py", "purpose": "Single file script", "instructions": task}]
# # # #             }
# # # # """
# # # #
# # # # # --- DOSYALARI YAZ ---
# # # # base_path = "libs/agents/src/multi_ai/agents"
# # # #
# # # # files = {
# # # #     f"{base_path}/researcher.py": researcher_code,
# # # #     f"{base_path}/architect.py": architect_code
# # # # }
# # # #
# # # # for path, content in files.items():
# # # #     os.makedirs(os.path.dirname(path), exist_ok=True)
# # # #     with open(path, "w", encoding="utf-8") as f:
# # # #         f.write(content.strip())
# # # #     print(f"✅ Düzeltildi: {path}")
# # # #
# # # # print("✨ Tüm eksik importlar eklendi.")
# # #
# # #
# # # import asyncio
# # # from temporalio.client import Client
# # #
# # #
# # # async def main():
# # #     print("🔌 Temporal'a bağlanılıyor...")
# # #     client = await Client.connect("localhost:7233")
# # #
# # #     print("🔍 Çalışan (Running) iş akışları taranıyor...")
# # #
# # #     # Sadece 'Running' statüsündeki işleri listele
# # #     count = 0
# # #     async for workflow in client.list_workflows('ExecutionStatus="Running"'):
# # #         w_id = workflow.id
# # #         r_id = workflow.run_id
# # #
# # #         try:
# # #             handle = client.get_workflow_handle(w_id, run_id=r_id)
# # #             await handle.terminate("Otomatik Temizlik 🧹")
# # #             print(f"✅ SONLANDIRILDI: {w_id} (RunID: {r_id})")
# # #             count += 1
# # #         except Exception as e:
# # #             # Eğer tam o sırada bittiyse hatayı yut ve devam et
# # #             print(f"⚠️ Zaten bitmiş: {w_id}")
# # #
# # #     if count == 0:
# # #         print("🎉 Temiz! Şu an çalışan hiç iş akışı yok.")
# # #     else:
# # #         print(f"🏁 Toplam {count} adet zombi süreç temizlendi.")
# # #
# # #
# # # if __name__ == "__main__":
# # #     asyncio.run(main())
# #
# #
# # import asyncio
# # import sys
# # import os
# #
# # # Proje yolunu ekle
# # sys.path.append(os.path.join(os.path.dirname(__file__), 'libs', 'utils', 'src'))
# #
# # from multi_ai.utils.robust_ollama_client import RobustOllamaClient
# #
# # async def test_ollama_client():
# #     print('🧪 RobustOllamaClient testi başlıyor...')
# #     client = RobustOllamaClient()
# #     try:
# #         result = await client.generate(
# #             model='deepseek-coder:6.7b',
# #             prompt='print hello world in python',
# #             options={'temperature': 0.2}
# #         )
# #         print('✅ BAŞARILI! Sonuç:')
# #         print(f'Response: {result.get(\"response\", \"No response\")}')
# #         return True
# #     except Exception as e:
# #         print(f'❌ HATA: {e}')
# #         import traceback
# #         traceback.print_exc()
# #         return False
# #
# # # Testi çalıştır
# # success = asyncio.run(test_ollama_client())
# # print(f'🎯 Test sonucu: {\"BAŞARILI\" if success else \"BAŞARISIZ\"}')
# # "
#
#
# import os
#
# # Worker ile %100 uyumlu, Pydantic V2 formatında Settings dosyası
# SETTINGS_CONTENT = """from pydantic_settings import BaseSettings
# from pydantic import Field, ConfigDict
# from typing import Optional
# from pathlib import Path
#
# class KMSSettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     provider: str = Field(default='local')
#     endpoint: Optional[str] = None
#     token: Optional[str] = None
#     mount_path: str = Field(default='secret')
#
# class DatabaseSettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     url: str = 'postgresql://temporal:temporal@localhost:5432/temporal'
#     pool_size: int = 20
#     echo: bool = False
#
# class RedisSettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     url: str = 'redis://localhost:6379'
#     stream_key: str = 'multi_ai:events'
#     consumer_group: str = 'multi_ai_workers'
#     consumer_name: str = 'worker_01'
#
# class TemporalSettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     namespace: str = 'default'
#     address: str = 'localhost:7233'
#     task_queue: str = 'multi-ai-tasks'
#
# class ObservabilitySettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     enabled: bool = True
#     endpoint: Optional[str] = None
#     service_name: str = 'multi-ai-platform'
#     service_version: str = '5.1.0'
#     log_level: str = 'INFO'
#
# # --- DÜZELTİLEN KISIM: OLLAMA AYARLARI ---
# class OllamaSettings(BaseSettings):
#     model_config = ConfigDict(extra='ignore')
#     # Windows için 127.0.0.1 zorunlu, /v1 kaldırıldı
#     base_url: str = 'http://127.0.0.1:11434'
#     default_model: str = 'llama3.2:1b'
#     coder_model: str = 'deepseek-coder:6.7b'
#     temperature: float = 0.2
#
# class PlatformSettings(BaseSettings):
#     model_config = ConfigDict(env_prefix='MULTI_AI_', case_sensitive=False, extra='ignore')
#
#     environment: str = 'development'
#     debug: bool = True
#     log_format: str = 'json'
#
#     kms: KMSSettings = Field(default_factory=KMSSettings)
#     database: DatabaseSettings = Field(default_factory=DatabaseSettings)
#     redis: RedisSettings = Field(default_factory=RedisSettings)
#     temporal: TemporalSettings = Field(default_factory=TemporalSettings)
#     observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
#
#     # ARTIK 'llm' YERİNE 'ollama' KULLANILIYOR
#     ollama: OllamaSettings = Field(default_factory=OllamaSettings)
#
#     github_app_id: Optional[str] = None
#     github_private_key: Optional[str] = None
#     github_webhook_secret: Optional[str] = "dummy_secret"
#
#     base_dir: Path = Path.cwd()
#     cache_dir: Path = Path.cwd() / '.cache'
#
# settings = PlatformSettings()
# """
#
# # Dosyayı yaz
# file_path = "libs/core/src/multi_ai/core/settings.py"
# os.makedirs(os.path.dirname(file_path), exist_ok=True)
#
# with open(file_path, "w", encoding="utf-8") as f:
#     f.write(SETTINGS_CONTENT)
#
# print(f"✅ {file_path} başarıyla güncellendi! (LLM -> Ollama dönüşümü yapıldı)")

import asyncio
from temporalio.client import Client

async def main():
    print("🔌 Zombiler temizleniyor...")
    client = await Client.connect("localhost:7233")
    async for wf in client.list_workflows('ExecutionStatus="Running"'):
        await client.get_workflow_handle(wf.id, run_id=wf.run_id).terminate("Clean Restart")
        print(f"💀 Öldürüldü: {wf.id}")

