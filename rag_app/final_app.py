"""Final simplified RAG application - Works without external API calls in restricted environments."""
import logging
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive knowledge base about AI/ML
articles_db = [
    {
        "title": "Introduction to Machine Learning",
        "content": """Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves. The main types of machine learning are:

1. Supervised Learning: Learning from labeled data
2. Unsupervised Learning: Finding patterns in unlabeled data
3. Reinforcement Learning: Learning through trial and error

Machine learning is used in recommendation systems, image recognition, natural language processing, and many other applications.""",
        "source": "AI Knowledge Base",
        "category": "Machine Learning",
        "url": "https://example.com/ml-intro"
    },
    {
        "title": "Deep Learning Fundamentals",
        "content": """Deep learning is a subset of machine learning that uses neural networks with multiple layers (hence 'deep'). These neural networks attempt to simulate the behavior of the human brain to 'learn' from large amounts of data.

Key concepts in deep learning:
- Neural Networks: Layers of interconnected nodes
- Backpropagation: Method for training networks
- Activation Functions: Non-linear transformations
- Convolutional Networks (CNNs): For image processing
- Recurrent Networks (RNNs): For sequence data

Deep learning powers many modern AI applications including computer vision, speech recognition, natural language processing, and autonomous vehicles.""",
        "source": "AI Knowledge Base",
        "category": "Deep Learning",
        "url": "https://example.com/deep-learning"
    },
    {
        "title": "Natural Language Processing (NLP) Overview",
        "content": """Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language. NLP combines computational linguistics with machine learning and deep learning.

Common NLP tasks:
- Text Classification: Categorizing text into predefined categories
- Named Entity Recognition: Identifying entities like names, places
- Sentiment Analysis: Determining emotional tone
- Machine Translation: Translating between languages
- Question Answering: Answering questions from text
- Text Summarization: Creating concise summaries

Modern NLP uses transformer models like BERT, GPT, and others that have revolutionized language understanding.""",
        "source": "AI Knowledge Base",
        "category": "NLP",
        "url": "https://example.com/nlp"
    },
    {
        "title": "Retrieval Augmented Generation (RAG) Explained",
        "content": """Retrieval Augmented Generation (RAG) is a technique that combines retrieval-based and generation-based approaches in AI systems. It's particularly useful for large language models.

How RAG works:
1. Retrieval: Search for relevant documents from a knowledge base
2. Augmentation: Add retrieved context to the query
3. Generation: Use an LLM to generate a response with the context

Benefits of RAG:
- Reduces hallucinations by grounding responses in facts
- Provides source attribution and citations
- Enables knowledge updates without retraining the model
- More cost-effective than fine-tuning for domain knowledge
- Maintains model accuracy with up-to-date information

RAG is used in chatbots, question-answering systems, and information retrieval applications.""",
        "source": "AI Knowledge Base",
        "category": "RAG",
        "url": "https://example.com/rag"
    },
    {
        "title": "Large Language Models (LLMs) Explained",
        "content": """Large Language Models (LLMs) are AI models trained on vast amounts of text data to understand and generate human-like text. Examples include GPT-4, Claude, Gemini, and LLaMA.

Key characteristics:
- Billions of parameters (weights)
- Trained on diverse internet text
- Can perform many tasks without specific training
- Use transformer architecture
- Exhibit emergent abilities at scale

Applications:
- Content generation and writing assistance
- Code generation and debugging
- Translation and summarization
- Question answering and chat
- Data analysis and extraction

Challenges include computational costs, potential biases, hallucinations, and ensuring responsible use.""",
        "source": "AI Knowledge Base",
        "category": "LLMs",
        "url": "https://example.com/llms"
    },
    {
        "title": "Transformer Architecture in AI",
        "content": """The Transformer is a neural network architecture introduced in the paper 'Attention is All You Need' in 2017. It revolutionized NLP and forms the basis of modern LLMs.

Key components:
- Self-Attention Mechanism: Weighs importance of different words
- Multi-Head Attention: Multiple attention mechanisms in parallel
- Position Encodings: Captures word order information
- Feed-Forward Networks: Processes attention outputs
- Layer Normalization: Stabilizes training

Transformers enable parallel processing, handle long-range dependencies, and scale effectively with data and compute.""",
        "source": "AI Knowledge Base",
        "category": "Architecture",
        "url": "https://example.com/transformers"
    },
    {
        "title": "Embeddings and Vector Databases",
        "content": """Embeddings are dense vector representations of data (text, images, etc.) that capture semantic meaning. Vector databases store and search these embeddings efficiently.

Concepts:
- Word Embeddings: Representing words as vectors (Word2Vec, GloVe)
- Sentence Embeddings: Representing entire sentences
- Semantic Similarity: Measuring closeness in vector space
- Cosine Similarity: Common metric for comparing embeddings

Vector databases (ChromaDB, Pinecone, Weaviate) enable:
- Fast similarity search
- Semantic search capabilities
- RAG system implementations
- Recommendation systems""",
        "source": "AI Knowledge Base",
        "category": "Embeddings",
        "url": "https://example.com/embeddings"
    }
]

# Pydantic models
class QueryRequest(BaseModel):
    question: str

# FastAPI app
app = FastAPI(
    title="AI Knowledge RAG System",
    version="1.0.0",
    description="AI Knowledge Base with RAG capabilities"
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
    """Keyword-based search in articles."""
    query_lower = query.lower()
    scored_articles = []

    for article in articles_db:
        score = 0
        text = (article['title'] + " " + article['content'] + " " + article.get('category', '')).lower()

        # Score based on query words
        for word in query_lower.split():
            if len(word) > 2:  # Ignore very short words
                # Higher score for title matches
                score += text.count(word) * (2 if word in article['title'].lower() else 1)

        if score > 0:
            scored_articles.append((score, article))

    # Sort and return top_k
    scored_articles.sort(reverse=True, key=lambda x: x[0])
    return [article for _, article in scored_articles[:top_k]]


def generate_answer(question: str) -> Dict[str, Any]:
    """Generate answer from knowledge base."""
    relevant_articles = search_articles(question, top_k=3)

    if not relevant_articles:
        return {
            "answer": "I don't have information about that topic in my knowledge base. My knowledge covers Machine Learning, Deep Learning, NLP, RAG, LLMs, Transformers, and Embeddings. Try asking about these topics!",
            "sources": []
        }

    # Build answer from relevant articles
    answer_parts = []
    for i, article in enumerate(relevant_articles, 1):
        answer_parts.append(f"**{article['title']}**\n\n{article['content']}\n")

    answer = "Based on the knowledge base, here's what I found:\n\n" + "\n---\n\n".join(answer_parts[:2])

    return {
        "answer": answer,
        "sources": [
            {
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                "category": article.get("category", "")
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
        "articles_count": len(articles_db),
        "ready": True
    }


@app.get("/api/stats")
async def stats():
    """Get statistics."""
    categories = {}
    for article in articles_db:
        cat = article.get('category', 'General')
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_documents": len(articles_db),
        "categories": categories,
        "embedding_model": "Keyword-based search",
        "sources": {"AI Knowledge Base": len(articles_db)}
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query the knowledge base."""
    logger.info(f"Query: {request.question}")
    result = generate_answer(request.question)

    return {
        "mode": "answer",
        "question": request.question,
        "num_sources": len(result.get("sources", [])),
        **result
    }


@app.post("/api/fetch-articles")
async def fetch_articles():
    """Articles are pre-loaded."""
    return {
        "status": "success",
        "message": f"Knowledge base contains {len(articles_db)} expert articles on AI/ML topics",
        "total_articles": len(articles_db)
    }


@app.delete("/api/clear")
async def clear():
    """Mock clear."""
    return {"status": "info", "message": "Knowledge base is read-only"}


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 AI KNOWLEDGE RAG SYSTEM - NOW RUNNING!")
    print("="*80)
    print(f"\n✅ Server is LIVE at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"💾 Pre-loaded with {len(articles_db)} comprehensive AI/ML articles\n")
    print("📖 Topics covered:")
    for article in articles_db:
        print(f"   • {article['title']}")
    print("\n💡 Example questions to try:")
    print("   • What is machine learning?")
    print("   • Explain RAG and how it works")
    print("   • What are large language models?")
    print("   • How do transformers work?")
    print("   • Tell me about embeddings")
    print("\n" + "="*80)
    print("🌐 Open http://localhost:8000 in your browser to use the chat interface!")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
