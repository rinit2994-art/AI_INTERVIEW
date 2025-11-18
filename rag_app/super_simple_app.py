"""Ultra-simplified RAG application - No external article fetching."""
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded API Key
GEMINI_API_KEY = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Sample articles about AI/ML (pre-loaded knowledge base)
articles_db = [
    {
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves.",
        "source": "Sample Data",
        "url": "https://example.com/ml-intro"
    },
    {
        "title": "Deep Learning Fundamentals",
        "content": "Deep learning is a subset of machine learning that uses neural networks with multiple layers. These neural networks attempt to simulate the behavior of the human brain to 'learn' from large amounts of data. Deep learning drives many AI applications including image recognition, natural language processing, and autonomous vehicles.",
        "source": "Sample Data",
        "url": "https://example.com/deep-learning"
    },
    {
        "title": "Natural Language Processing Overview",
        "content": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret and manipulate human language. NLP draws from many disciplines, including computer science and computational linguistics, to bridge the gap between human communication and computer understanding.",
        "source": "Sample Data",
        "url": "https://example.com/nlp"
    },
    {
        "title": "Retrieval Augmented Generation (RAG)",
        "content": "RAG is a technique that combines retrieval-based and generation-based approaches in AI systems. It works by first retrieving relevant documents from a knowledge base, then using those documents as context to generate more accurate and informative responses. This approach helps reduce hallucinations and provides source attribution.",
        "source": "Sample Data",
        "url": "https://example.com/rag"
    },
    {
        "title": "Large Language Models Explained",
        "content": "Large Language Models (LLMs) are AI models trained on vast amounts of text data to understand and generate human-like text. Examples include GPT-4, Claude, and Gemini. They excel at tasks like content generation, translation, summarization, and question-answering.",
        "source": "Sample Data",
        "url": "https://example.com/llms"
    }
]

# Pydantic models
class QueryRequest(BaseModel):
    question: str

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
                score += text.count(word) * 10

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
        # Fallback to direct Gemini answer
        try:
            response = model.generate_content(f"Answer this question about AI/ML: {question}")
            return {
                "answer": response.text,
                "sources": []
            }
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }

    # Build context from relevant articles
    context = "\n\n".join([
        f"Source: {article['title']}\n{article['content']}"
        for article in relevant_articles
    ])

    # Create prompt for Gemini
    prompt = f"""You are an AI assistant specialized in Artificial Intelligence, Machine Learning, and Data Science.

Use the following context to answer the question. Be comprehensive and cite the sources.

Context:
{context}

Question: {question}

Provide a detailed answer based on the context above.

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
        "service": "AI Knowledge RAG System (Simplified)",
        "articles_count": len(articles_db)
    }


@app.get("/api/stats")
async def stats():
    """Get statistics."""
    return {
        "total_documents": len(articles_db),
        "sources": {"Sample Data": len(articles_db)},
        "embedding_model": "Simple keyword search"
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query the knowledge base."""
    result = generate_answer_with_rag(request.question)
    return {
        "mode": "answer",
        "question": request.question,
        "num_sources": len(result.get("sources", [])),
        **result
    }


@app.post("/api/fetch-articles")
async def fetch_articles():
    """Mock fetch - articles are pre-loaded."""
    return {
        "status": "success",
        "message": f"Using {len(articles_db)} pre-loaded sample articles",
        "total_articles": len(articles_db)
    }


@app.delete("/api/clear")
async def clear():
    """Mock clear."""
    return {"status": "success", "message": "Using sample data"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 AI Knowledge RAG System (Simplified) Starting...")
    print("="*70)
    print(f"\n📍 Server URL: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"💡 Pre-loaded with {len(articles_db)} sample AI/ML articles")
    print(f"🤖 Powered by Google Gemini AI\n")
    print("Try asking:")
    print("  - What is machine learning?")
    print("  - Explain RAG")
    print("  - What are large language models?")
    print("\n" + "="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
