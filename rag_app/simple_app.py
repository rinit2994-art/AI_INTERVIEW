"""Simplified RAG application without heavy dependencies."""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import feedparser
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded API Key
GEMINI_API_KEY = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Simple in-memory storage for articles
articles_db: List[Dict[str, Any]] = []

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

# FastAPI app
app = FastAPI(
    title="AI Knowledge RAG System",
    version="1.0.0",
    description="Simple RAG system powered by Gemini AI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_articles_from_sources() -> List[Dict[str, Any]]:
    """Fetch articles from RSS feeds."""
    all_articles = []

    sources = [
        ("https://blog.research.google/feeds/posts/default", "Google AI Blog"),
        ("https://towardsdatascience.com/feed", "Towards Data Science"),
    ]

    # Medium tags
    medium_tags = ["artificial-intelligence", "machine-learning", "data-science", "generative-ai"]

    for tag in medium_tags[:2]:  # Limit to 2 tags for speed
        sources.append((f"https://medium.com/feed/tag/{tag}", f"Medium ({tag})"))

    for rss_url, source_name in sources:
        try:
            logger.info(f"Fetching from {source_name}")
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:5]:  # Limit to 5 articles per source
                content = entry.get('summary', entry.get('description', ''))
                if content:
                    all_articles.append({
                        "title": entry.title,
                        "content": content[:1000],  # Limit content length
                        "url": entry.link,
                        "source": source_name,
                        "published_date": entry.get("published", ""),
                        "fetched_date": datetime.now().isoformat()
                    })
                    logger.info(f"  ✓ {entry.title[:50]}...")

        except Exception as e:
            logger.error(f"Error fetching {source_name}: {e}")

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles


def search_articles(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Simple keyword search in articles."""
    query_lower = query.lower()
    scored_articles = []

    for article in articles_db:
        score = 0
        text = (article['title'] + " " + article['content']).lower()

        # Simple scoring based on query words
        for word in query_lower.split():
            if len(word) > 3:  # Ignore short words
                score += text.count(word)

        if score > 0:
            scored_articles.append((score, article))

    # Sort by score and return top_k
    scored_articles.sort(reverse=True, key=lambda x: x[0])
    return [article for _, article in scored_articles[:top_k]]


def generate_answer_with_rag(question: str) -> Dict[str, Any]:
    """Generate answer using RAG with Gemini."""
    # Search for relevant articles
    relevant_articles = search_articles(question, top_k=3)

    if not relevant_articles:
        return {
            "answer": "I don't have enough information in my knowledge base to answer this question. Please try fetching more articles first.",
            "sources": []
        }

    # Build context from relevant articles
    context = "\n\n".join([
        f"Source: {article['title']} ({article['source']})\n{article['content'][:500]}"
        for article in relevant_articles
    ])

    # Create prompt for Gemini
    prompt = f"""You are an AI assistant specialized in Artificial Intelligence, Machine Learning, and Data Science.

Use the following context from recent articles to answer the question.

Context:
{context}

Question: {question}

Provide a comprehensive answer based on the context above. If the context doesn't contain enough information, say so.

Answer:"""

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        answer = f"Error generating answer: {str(e)}"

    return {
        "answer": answer,
        "sources": [
            {
                "title": article["title"],
                "url": article["url"],
                "source": article["source"]
            }
            for article in relevant_articles
        ]
    }


# Routes
@app.get("/")
async def root():
    """Serve frontend."""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "service": "AI Knowledge RAG System",
        "articles_count": len(articles_db)
    }


@app.get("/api/stats")
async def stats():
    """Get statistics."""
    sources = {}
    for article in articles_db:
        source = article['source']
        sources[source] = sources.get(source, 0) + 1

    return {
        "total_documents": len(articles_db),
        "sources": sources,
        "embedding_model": "Simple keyword search"
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query the knowledge base."""
    result = generate_answer_with_rag(request.question)
    return {
        "mode": "answer",
        "question": request.question,
        **result
    }


@app.post("/api/fetch-articles")
async def fetch_articles():
    """Fetch new articles."""
    global articles_db

    try:
        new_articles = await fetch_articles_from_sources()
        articles_db.extend(new_articles)

        return {
            "status": "success",
            "message": f"Fetched {len(new_articles)} articles",
            "total_articles": len(articles_db)
        }
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear")
async def clear():
    """Clear all articles."""
    global articles_db
    articles_db = []
    return {"status": "success", "message": "Database cleared"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 AI Knowledge RAG System Starting...")
    print("="*60)
    print(f"\n📍 Server will start at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"💡 Tip: Click 'Fetch New Articles' to populate the database\n")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
