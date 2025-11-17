"""FastAPI main application."""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from config.settings import settings
from backend.services.article_fetcher import ArticleFetcher
from backend.services.vector_store import get_vector_store
from backend.services.rag_pipeline import get_rag_pipeline
from backend.agents.adk_agents import get_adk_agent_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    mode: Optional[str] = "answer"  # "search", "answer", or "auto"
    top_k: Optional[int] = 5


class FetchRequest(BaseModel):
    force: Optional[bool] = False


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    num_sources: int
    question: str


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    logger.info("Starting AI Knowledge RAG System")

    # Initialize services
    try:
        vector_store = get_vector_store()
        rag_pipeline = get_rag_pipeline()
        adk_system = get_adk_agent_system()

        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

    yield

    logger.info("Shutting down AI Knowledge RAG System")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic RAG system for AI/ML knowledge retrieval",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def root():
    """Root endpoint - serves the frontend."""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query(request: QueryRequest):
    """
    Query the knowledge base.

    Modes:
    - search: Just return relevant documents
    - answer: Generate an answer with RAG (default)
    - auto: Let the ADK agent decide how to respond
    """
    try:
        if request.mode == "search":
            # Direct search
            vector_store = get_vector_store()
            results = vector_store.search(request.question, k=request.top_k)

            return {
                "mode": "search",
                "query": request.question,
                "results": results
            }

        elif request.mode == "answer":
            # RAG answer
            rag_pipeline = get_rag_pipeline()
            result = rag_pipeline.answer_question(request.question)

            return {
                "mode": "answer",
                **result
            }

        elif request.mode == "auto":
            # Agentic mode with ADK
            adk_system = get_adk_agent_system()
            result = await adk_system.process_query(request.question, mode="auto")

            return result

        else:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fetch-articles")
async def fetch_articles(request: FetchRequest, background_tasks: BackgroundTasks):
    """
    Fetch new articles from configured sources.
    This runs in the background.
    """
    try:
        async def fetch_and_store():
            """Background task to fetch and store articles."""
            try:
                logger.info("Starting article fetch task")

                async with ArticleFetcher() as fetcher:
                    articles = await fetcher.fetch_all_sources()

                if articles:
                    vector_store = get_vector_store()
                    num_added = vector_store.add_documents(articles)
                    logger.info(f"Added {num_added} document chunks to knowledge base")
                else:
                    logger.warning("No articles fetched")

            except Exception as e:
                logger.error(f"Error in fetch task: {e}")

        # Add task to background
        background_tasks.add_task(fetch_and_store)

        return {
            "status": "started",
            "message": "Article fetching started in background"
        }

    except Exception as e:
        logger.error(f"Error starting fetch task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """Get configured article sources."""
    return {
        "medium_tags": settings.medium_tags,
        "arxiv_categories": settings.arxiv_categories,
        "sources": [
            "Medium",
            "arXiv",
            "Towards Data Science",
            "Google AI Blog"
        ]
    }


@app.delete("/api/clear")
async def clear_database():
    """Clear all documents from the database (use with caution)."""
    try:
        vector_store = get_vector_store()
        vector_store.clear_database()

        return {
            "status": "success",
            "message": "Database cleared successfully"
        }

    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
