import logging
import os
from pathlib import Path
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class CodeKnowledgeBase:
    def __init__(self, collection_name="codebase_v1"):
        # Connect to Qdrant Docker container
        self.client = QdrantClient(host="localhost", port=6333)
        # Embedding model (Fast and lightweight)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = collection_name
        self._init_collection()

    def _init_collection(self):
        try:
            self.client.get_collection(self.collection)
        except:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            logger.info(f"🧠 Knowledge Base initialized: {self.collection}")

    def ingest_codebase(self, root_path: str):
        documents = []
        metadatas = []
        ids = []
        id_counter = 0

        print(f"📂 Scanning {root_path}...")

        for root, _, files in os.walk(root_path):
            # Skip unnecessary directories
            if any(ignore in root for ignore in [".venv", ".git", "__pycache__", ".idea", ".cache"]):
                continue
                
            for file in files:
                if file.endswith(".py") or file.endswith(".md") or file.endswith(".toml"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        if len(content.strip()) == 0: continue

                        documents.append(content[:5000]) # Truncate large files
                        metadatas.append({"path": file_path, "filename": file})
                        ids.append(id_counter)
                        id_counter += 1
                    except Exception as e:
                        print(f"⚠️ Skipped {file}: {e}")
        
        if not documents:
            print("❌ No documents found to ingest!")
            return

        print(f"🧠 Embedding {len(documents)} files into Vector DB...")
        embeddings = self.encoder.encode(documents)
        
        self.client.upsert(
            collection_name=self.collection,
            points=models.Batch(
                ids=ids,
                vectors=embeddings.tolist(),
                payloads=metadatas
            )
        )
        print("✅ Ingestion Complete! Agent memory upgraded.")

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        query_vector = self.encoder.encode(query).tolist()
        
        # UPDATED: Use query_points instead of search
        # query_points returns a QueryResponse object containing a 'points' list
        response = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=limit
        )
        
        results = []
        # Access points from the response
        for hit in response.points:
            results.append({
                "path": hit.payload["path"],
                "score": hit.score,
                "content": hit.payload.get("content", "") 
            })
        return results

rag_engine = CodeKnowledgeBase()
