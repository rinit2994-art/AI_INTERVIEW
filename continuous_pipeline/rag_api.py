"""
RAG API - Query ChromaDB with Gemini LLM
FastAPI server for semantic search and answer generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Optional
import google.generativeai as genai
from chromadb_manager import ChromaDBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Continuous Pipeline RAG API",
    description="Semantic search over continuously updated web content"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
GEMINI_API_KEY = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"
genai.configure(api_key=GEMINI_API_KEY)

db_manager = ChromaDBManager(persist_directory="./chroma_db")
model = genai.GenerativeModel("gemini-1.5-flash")

logger.info("✅ RAG API initialized")


class QueryRequest(BaseModel):
    question: str
    n_results: int = 5


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5


@app.get("/")
async def home():
    """Home endpoint"""
    return {
        "service": "Continuous Pipeline RAG API",
        "status": "running",
        "endpoints": {
            "query": "/api/query - RAG with LLM answer generation",
            "search": "/api/search - Semantic search only",
            "stats": "/api/stats - Database statistics",
            "health": "/api/health - Health check"
        }
    }


@app.get("/api/health")
async def health():
    """Health check"""
    stats = db_manager.get_stats()

    return {
        "status": "healthy",
        "chromadb": {
            "total_documents": stats['total_documents'],
            "embedding_model": stats['embedding_model'],
            "embedding_dimension": stats['embedding_dimension']
        },
        "sources": stats.get('sources', {})
    }


@app.get("/api/stats")
async def stats():
    """Get database statistics"""
    stats = db_manager.get_stats()

    return {
        "total_documents": stats['total_documents'],
        "embedding_model": stats['embedding_model'],
        "embedding_dimension": stats['embedding_dimension'],
        "sources": stats.get('sources', {}),
        "storage": "ChromaDB with persistent storage"
    }


@app.post("/api/search")
async def search(request: SearchRequest):
    """
    Semantic search only (no LLM)

    Returns documents most similar to query
    """
    try:
        results = db_manager.query(request.query, n_results=request.n_results)

        if not results['documents']:
            return {
                "query": request.query,
                "results": [],
                "message": "No results found"
            }

        # Format results
        formatted_results = []
        for doc, dist, meta in zip(
            results['documents'],
            results['distances'],
            results['metadatas']
        ):
            formatted_results.append({
                'content': doc,
                'distance': float(dist),
                'metadata': meta
            })

        return {
            "query": request.query,
            "results": formatted_results,
            "total": len(formatted_results)
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query(request: QueryRequest):
    """
    RAG Query - Semantic search + LLM answer generation

    1. Search ChromaDB for relevant documents
    2. Use Gemini to generate comprehensive answer
    """
    try:
        # Step 1: Semantic search
        search_results = db_manager.query(
            request.question,
            n_results=request.n_results
        )

        if not search_results['documents']:
            return {
                "question": request.question,
                "answer": "No relevant information found in the knowledge base.",
                "sources": []
            }

        # Step 2: Build context from top documents
        context_parts = []
        sources = []

        for i, (doc, dist, meta) in enumerate(zip(
            search_results['documents'],
            search_results['distances'],
            search_results['metadatas']
        ), 1):
            context_parts.append(f"Document {i} [{meta['source']}]:\n{doc}\n")

            sources.append({
                'title': meta.get('title', 'No title'),
                'url': meta.get('url', ''),
                'source': meta.get('source', ''),
                'distance': float(dist),
                'content_preview': doc[:200]
            })

        context = "\n".join(context_parts)

        # Step 3: Generate answer with Gemini
        prompt = f"""You are a helpful AI assistant. Answer the following question using ONLY the information from the provided context.

QUESTION: {request.question}

CONTEXT:
{context}

INSTRUCTIONS:
- Provide a comprehensive, well-structured answer
- Use information from the context above
- If the context doesn't contain relevant information, say so
- Include specific details and examples from the documents
- Cite sources when relevant (e.g., "According to [source]...")
- Be factual and accurate
- NO TRUNCATION - provide complete answer

ANSWER:"""

        response = model.generate_content(prompt)
        answer = response.text

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources,
            "metadata": {
                "total_sources": len(sources),
                "embedding_model": "all-mpnet-base-v2",
                "llm_model": "gemini-1.5-flash"
            }
        }

    except Exception as e:
        logger.error(f"Query error: {e}")
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🤖 CONTINUOUS PIPELINE RAG API")
    print("="*80)
    print("\n✨ Features:")
    print("  • Semantic search with all-mpnet-base-v2 embeddings")
    print("  • RAG with Gemini 1.5 Flash")
    print("  • Continuously updated knowledge base")
    print("  • Multi-source content (HackerNews, arXiv, GitHub, Medium, etc.)")
    print("\n📊 Endpoints:")
    print("  • GET  / - API info")
    print("  • GET  /api/health - Health check")
    print("  • GET  /api/stats - Database statistics")
    print("  • POST /api/search - Semantic search only")
    print("  • POST /api/query - RAG query (search + LLM answer)")
    print("\n🌐 Server: http://localhost:8001")
    print("="*80 + "\n")

    stats = db_manager.get_stats()
    print(f"📚 Current database: {stats['total_documents']} documents")
    print(f"🔗 Sources: {stats.get('sources', {})}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8001)
