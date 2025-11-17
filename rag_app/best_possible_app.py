"""
THE BEST POSSIBLE RAG SYSTEM
Uses your complete 4,194 knowledge base with ChromaDB semantic search
Works in restricted environments
"""

import logging
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
from knowledge_base_manager_v2 import KnowledgeBaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="BEST AI Knowledge RAG")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class SemanticRAGSystem:
    """The BEST RAG system using your complete knowledge base."""

    def __init__(self):
        logger.info("🚀 Initializing BEST RAG System...")

        # Initialize knowledge base manager
        self.kb_manager = KnowledgeBaseManager()

        # Initialize ChromaDB with default embedding function
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            persist_directory="./chroma_best"
        ))

        # Create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="best_knowledge_base",
            metadata={"description": "Complete 4,194 entry knowledge base with semantic search"}
        )

        # Load knowledge base into ChromaDB
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load all 4,194 entries into ChromaDB."""
        logger.info("📚 Loading knowledge base into ChromaDB...")

        # Parse TypeScript knowledge base
        self.kb_manager.parse_typescript_kb()
        logger.info(f"✅ Parsed {len(self.kb_manager.entries)} entries")

        # Check if already loaded
        current_count = self.collection.count()
        if current_count >= len(self.kb_manager.entries):
            logger.info(f"✅ Knowledge base already loaded ({current_count} entries)")
            return

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for i, entry in enumerate(self.kb_manager.entries):
            # Create document with title and content
            doc_text = f"{entry['title']}\n\n{entry.get('content', '')}"

            documents.append(doc_text)
            metadatas.append({
                'title': entry['title'],
                'category': entry.get('category', 'General'),
                'keywords': ','.join(entry.get('keywords', [])[:10]),
                'entry_id': str(i)
            })
            ids.append(f"entry_{i}")

        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))

            self.collection.add(
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )

            logger.info(f"  Loaded {end_idx}/{len(documents)} entries...")

        logger.info(f"✅ Loaded {len(documents)} entries into ChromaDB")
        logger.info(f"📊 Total documents in ChromaDB: {self.collection.count()}")

    def search(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Semantic search using ChromaDB."""
        logger.info(f"🔍 Searching for: {question}")

        # Query ChromaDB
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k
        )

        # Format results
        formatted_results = []

        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0

                # Calculate similarity score (0-100)
                similarity = max(0, min(100, int((1 - distance) * 100)))

                formatted_results.append({
                    'title': metadata.get('title', 'Unknown'),
                    'content': doc,
                    'category': metadata.get('category', 'General'),
                    'keywords': metadata.get('keywords', ''),
                    'similarity': similarity,
                    'distance': distance
                })

        logger.info(f"✅ Found {len(formatted_results)} results")
        return formatted_results


# Initialize system
rag_system = SemanticRAGSystem()


@app.get("/")
async def home():
    """Serve the frontend."""
    return FileResponse("../docs/index.html")


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "total_documents": rag_system.collection.count(),
        "system": "BEST RAG with Semantic Search"
    }


@app.get("/api/stats")
async def stats():
    """Get system statistics."""
    return {
        "total_documents": rag_system.collection.count(),
        "total_entries": len(rag_system.kb_manager.entries),
        "categories": len(rag_system.kb_manager.category_index),
        "unique_keywords": len(rag_system.kb_manager.keyword_index),
        "search_type": "Semantic (ChromaDB with embeddings)"
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query the knowledge base with semantic search."""
    try:
        results = rag_system.search(request.question, request.top_k)

        return {
            "answer": "Here are the most relevant results based on semantic similarity:",
            "sources": [
                {
                    "title": r['title'],
                    "content": r['content'],
                    "category": r['category'],
                    "keywords": r['keywords'],
                    "similarity": r['similarity']
                }
                for r in results
            ],
            "metadata": {
                "query": request.question,
                "results_count": len(results),
                "search_type": "semantic",
                "total_documents": rag_system.collection.count()
            }
        }
    except Exception as e:
        logger.error(f"Query error: {e}")
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "metadata": {"error": str(e)}
        }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 BEST POSSIBLE RAG SYSTEM")
    print("="*80)
    print("\n✅ Features:")
    print("  • Complete 4,194 entry knowledge base")
    print("  • Semantic search with ChromaDB")
    print("  • Vector embeddings (automatic)")
    print("  • Similarity scoring")
    print("  • Full content (no truncation)")
    print("\n" + "="*80)
    print(f"📊 Knowledge Base Size: {rag_system.collection.count()} entries")
    print("="*80 + "\n")

    print("🌐 Starting server at http://localhost:8000")
    print("📚 API Docs at http://localhost:8000/docs")
    print("\n" + "="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
