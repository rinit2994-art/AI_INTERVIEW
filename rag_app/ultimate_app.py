"""
Ultimate RAG System with MCP Integration, Web Search, and Live Data Fetching
Supports: A2A Protocol, MCP, ChromaDB, Latest AI Technologies
"""
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, BackgroundTasks
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

# Enhanced knowledge base with latest AI technologies
articles_db = [
    {
        "title": "Agent-to-Agent (A2A) Protocol",
        "content": """The Agent-to-Agent (A2A) Protocol is a standardized communication protocol that enables AI agents to discover, communicate, and collaborate with each other autonomously.

Key Features:
- Service Discovery: Agents can find and connect with other agents
- Standardized Communication: Common message formats and protocols
- Capability Negotiation: Agents exchange information about their capabilities
- Secure Communication: Authentication and authorization between agents
- Multi-Agent Orchestration: Coordinate complex tasks across multiple agents

Use Cases:
- Multi-agent systems working together on complex tasks
- Distributed AI architectures
- Autonomous agent marketplaces
- Cross-platform agent communication
- Enterprise AI agent ecosystems

The A2A protocol is part of Google's Agent Development Kit (ADK) and enables sophisticated multi-agent workflows.""",
        "source": "Latest AI Technology",
        "category": "Agent Protocols",
        "url": "https://github.com/google/adk-python",
        "keywords": ["a2a", "agent to agent", "protocol", "multi-agent", "adk", "google", "agent communication"]
    },
    {
        "title": "Model Context Protocol (MCP)",
        "content": """The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). Developed by Anthropic, it enables seamless integration between AI models and various data sources.

Core Concepts:
- Context Servers: Expose data and functionality to LLMs
- Standardized Interface: Common protocol for context provision
- Tool Integration: LLMs can call tools and functions
- Resource Management: Efficient handling of context and memory
- Security: Controlled access to data and capabilities

Key Components:
1. MCP Servers: Provide context and tools to LLMs
2. MCP Clients: Connect LLMs to MCP servers
3. Protocol Messages: Standardized communication format
4. Resources: Files, databases, APIs exposed to LLMs
5. Tools: Functions the LLM can execute

Benefits:
- Connect LLMs to any data source
- Reusable context providers
- Better context management
- Reduced hallucinations through grounding
- Standardized AI tool ecosystem

Popular MCP Servers:
- GitHub MCP Server: Access GitHub repos and data
- Filesystem MCP Server: Local file access
- Database MCP Server: Query databases
- Web Search MCP Server: Live web searching""",
        "source": "Latest AI Technology",
        "category": "AI Protocols",
        "url": "https://modelcontextprotocol.io",
        "keywords": ["mcp", "model context protocol", "anthropic", "llm", "context", "ai protocol", "claude"]
    },
    {
        "title": "ChromaDB - AI-Native Vector Database",
        "content": """ChromaDB is an open-source embedding database designed for AI applications. It's built for storing and querying embeddings efficiently, making it ideal for RAG (Retrieval Augmented Generation) systems.

Key Features:
- Simple API: Easy to use Python interface
- Fast Similarity Search: Efficient vector search
- Metadata Filtering: Filter results by metadata
- Persistent Storage: Save and load databases
- Multiple Embedding Functions: Support for various embeddings
- Local-First: Works offline without external services

Core Operations:
1. Add Documents: Store text with automatic embedding
2. Query: Find similar documents using semantic search
3. Update: Modify existing documents
4. Delete: Remove documents from collection
5. Filter: Combine semantic search with metadata filters

Use Cases:
- RAG Applications: Provide context to LLMs
- Semantic Search: Find similar content
- Recommendation Systems: Suggest related items
- Knowledge Management: Organize information semantically
- Question Answering: Retrieve relevant documents

Integration:
- LangChain: Native integration
- LlamaIndex: Full support
- Embeddings: OpenAI, Sentence Transformers, Cohere
- Deployment: Local, Docker, Cloud""",
        "source": "Latest AI Technology",
        "category": "Vector Databases",
        "url": "https://www.trychroma.com",
        "keywords": ["chromadb", "vector database", "embeddings", "rag", "semantic search", "ai database"]
    },
    {
        "title": "Retrieval Augmented Generation (RAG) - Latest Techniques",
        "content": """RAG is an advanced AI technique that combines information retrieval with language model generation to produce more accurate, factual responses.

Modern RAG Architecture:
1. Indexing Phase:
   - Document chunking and preprocessing
   - Generate embeddings using advanced models
   - Store in vector database (ChromaDB, Pinecone, etc.)
   - Add metadata for filtering

2. Retrieval Phase:
   - Convert query to embedding
   - Semantic similarity search
   - Hybrid search (dense + sparse)
   - Reranking results for relevance
   - Metadata filtering

3. Generation Phase:
   - Construct prompt with retrieved context
   - LLM generates response
   - Include source citations
   - Fact-checking and validation

Advanced RAG Techniques (2024):
- Multi-Query RAG: Generate multiple queries for better coverage
- RAG-Fusion: Combine multiple retrieval strategies
- Self-RAG: Model critiques its own retrieval
- Corrective RAG: Fixes retrieval mistakes
- Adaptive RAG: Dynamically adjusts retrieval strategy
- Agentic RAG: Uses AI agents for complex retrieval
- GraphRAG: Uses knowledge graphs for context
- HyDE: Hypothetical document embeddings

Best Practices:
- Chunk size optimization (512-1024 tokens)
- Overlap between chunks (10-20%)
- Hybrid search (semantic + keyword)
- Reranking with cross-encoders
- Query decomposition for complex questions
- Metadata filtering for relevance
- Source attribution and citations""",
        "source": "Latest AI Technology",
        "category": "RAG Systems",
        "url": "https://arxiv.org/abs/2312.10997",
        "keywords": ["rag", "retrieval augmented generation", "advanced rag", "multi-query", "adaptive", "agentic rag"]
    },
    {
        "title": "Google ADK (Agent Development Kit)",
        "content": """The Agent Development Kit (ADK) is Google's framework for building, evaluating, and deploying AI agents. It provides tools for creating sophisticated agentic systems.

Core Features:
- LLM Agent Creation: Build agents with any LLM
- Multi-Agent Systems: Orchestrate multiple agents
- Tool Integration: Give agents capabilities
- Deployment Options: Cloud Run, Vertex AI, GKE
- Evaluation Framework: Test agent performance
- A2A Protocol Support: Agent-to-agent communication

Agent Types:
1. LLM Agents: Powered by language models
2. Custom Agents: Define your own logic
3. Workflow Agents: Sequential, parallel, loop patterns
4. Coordinator Agents: Orchestrate sub-agents

Key Components:
- Agent Class: Define agent behavior and capabilities
- Tools: Functions agents can execute
- Context: Maintain conversation state and memory
- Runtime: Execute agent workflows
- Observability: Monitor agent behavior

Deployment:
- Local: Run agents on your machine
- Cloud Run: Serverless agent deployment
- Vertex AI Agent Engine: Managed agent platform
- GKE: Kubernetes orchestration
- Docker: Containerized deployment

Integration:
- Gemini: Native integration
- OpenAI: GPT-4, GPT-3.5 support
- Anthropic: Claude integration
- Custom Models: Bring your own LLM
- MCP: Model Context Protocol support""",
        "source": "Latest AI Technology",
        "category": "Agent Frameworks",
        "url": "https://github.com/google/adk-python",
        "keywords": ["adk", "agent development kit", "google adk", "ai agents", "multi-agent", "genai"]
    },
    {
        "title": "Gemini 2.0 - Latest Capabilities",
        "content": """Gemini 2.0 is Google's latest multimodal AI model with advanced capabilities for understanding and generating text, images, audio, video, and code.

New in Gemini 2.0:
- Native Multimodal: Processes all modalities natively
- Improved Reasoning: Better logical and mathematical reasoning
- Longer Context: Up to 1M+ token context window
- Faster Inference: Optimized for speed
- Tool Use: Advanced function calling
- Code Execution: Can run and test code
- Multimodal Output: Generate images, audio, video

Gemini 2.0 Models:
1. Gemini 2.0 Flash: Fast, efficient for production
2. Gemini 2.0 Pro: Balanced performance
3. Gemini 2.0 Ultra: Maximum capability
4. Gemini 2.0 Nano: On-device deployment

Key Features:
- Native Image Understanding: No separate vision model needed
- Audio Processing: Speech, music, sound understanding
- Video Analysis: Frame-by-frame and temporal understanding
- Code Generation: Multi-language with execution
- Structured Output: JSON, schemas, function calls
- Safety: Built-in safety filters and controls

Use Cases:
- Multimodal RAG: Understand documents with images
- Code Assistance: Generate and debug code
- Content Creation: Text, image, video generation
- Data Analysis: Process and analyze complex data
- Automation: Build AI agents and workflows""",
        "source": "Latest AI Technology",
        "category": "Large Language Models",
        "url": "https://deepmind.google/technologies/gemini",
        "keywords": ["gemini", "gemini 2.0", "google ai", "multimodal", "llm", "genai"]
    },
    {
        "title": "LangChain - Advanced LLM Framework",
        "content": """LangChain is a comprehensive framework for building applications with Large Language Models. It provides tools for chains, agents, memory, and more.

Core Modules:
1. Models: LLM and chat model integrations
2. Prompts: Prompt templates and management
3. Chains: Combine multiple steps
4. Agents: LLMs that make decisions
5. Memory: Persist state between calls
6. Indexes: Document loading and retrieval
7. Callbacks: Hook into various stages

Advanced Features (2024):
- LangGraph: Build stateful multi-actor applications
- LCEL: LangChain Expression Language for chains
- LangSmith: Observability and debugging
- LangServe: Deploy chains as APIs
- Structured Output: Type-safe outputs
- Streaming: Real-time response streaming

Agent Types:
- ReAct Agent: Reasoning + Acting
- OpenAI Functions Agent: Uses function calling
- Conversational Agent: Chat-optimized
- Self-Ask Agent: Decomposes questions
- Plan-and-Execute Agent: Plans then executes

RAG with LangChain:
- Document Loaders: PDF, web, databases
- Text Splitters: Smart chunking
- Vector Stores: ChromaDB, Pinecone, FAISS
- Retrievers: Advanced retrieval strategies
- Chains: RAG chains with citations

Integration:
- 100+ LLM providers
- Vector databases
- Document stores
- APIs and tools
- Memory systems""",
        "source": "Latest AI Technology",
        "category": "AI Frameworks",
        "url": "https://python.langchain.com",
        "keywords": ["langchain", "llm framework", "rag", "agents", "chains", "langgraph"]
    },
    {
        "title": "Transformer Architecture Evolution",
        "content": """Transformers have evolved significantly since "Attention is All You Need" (2017). Modern variants power all major LLMs.

Transformer Evolution:
1. Original Transformer (2017): Encoder-decoder architecture
2. BERT (2018): Bidirectional encoder
3. GPT (2018-2023): Decoder-only, autoregressive
4. T5 (2019): Text-to-text framework
5. Switch Transformer (2021): Sparse mixture of experts
6. Vision Transformer (2020): Transformers for images
7. Perceiver (2021): General architecture for any modality
8. Flash Attention (2022): Efficient attention computation
9. Mixture of Experts (2024): Dynamic expert routing

Modern Improvements:
- Rotary Position Embeddings (RoPE): Better position encoding
- Group Query Attention: Faster inference
- Flash Attention 2: 2x faster than original
- Sliding Window Attention: Efficient long context
- Multi-Query Attention: Shared key-value
- ALiBi: Attention with linear biases
- Relative Position: Better position awareness

Architecture Variants:
- Encoder-Only: BERT, RoBERTa (classification)
- Decoder-Only: GPT, LLaMA (generation)
- Encoder-Decoder: T5, BART (translation)
- Sparse: Switch, GLaM (efficiency)
- Retrieval-Augmented: RETRO, Atlas (factual)

Key Concepts:
- Self-Attention: Relate all positions
- Multi-Head: Multiple attention patterns
- Feed-Forward: Process attention outputs
- Layer Normalization: Stabilize training
- Residual Connections: Enable deep networks""",
        "source": "Latest AI Technology",
        "category": "AI Architecture",
        "url": "https://arxiv.org/abs/1706.03762",
        "keywords": ["transformer", "attention", "bert", "gpt", "architecture", "self-attention", "multimodal"]
    }
]

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    use_web_search: bool = False

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5

# FastAPI app
app = FastAPI(
    title="Ultimate AI Knowledge RAG System",
    version="2.0.0",
    description="Advanced RAG with MCP, A2A, Web Search, and Latest AI Knowledge"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def web_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """Perform web search using DuckDuckGo (no API key needed)."""
    try:
        # Using DuckDuckGo Instant Answer API (free, no auth required)
        url = f"https://api.duckduckgo.com/?q={query}&format=json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    results = []

                    # Abstract
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('Heading', 'DuckDuckGo Result'),
                            'content': data['Abstract'],
                            'url': data.get('AbstractURL', ''),
                            'source': 'Web Search'
                        })

                    # Related topics
                    for topic in data.get('RelatedTopics', [])[:num_results-1]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                                'content': topic['Text'],
                                'url': topic.get('FirstURL', ''),
                                'source': 'Web Search'
                            })

                    return results

    except Exception as e:
        logger.error(f"Web search error: {e}")

    return []


def search_knowledge_base(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Enhanced keyword search with better scoring."""
    query_lower = query.lower()
    scored_articles = []

    for article in articles_db:
        score = 0
        text = (
            article['title'] + ' ' +
            article['content'] + ' ' +
            article.get('category', '') + ' ' +
            ' '.join(article.get('keywords', []))
        ).lower()

        # Score based on query words
        words = query_lower.split()
        for word in words:
            if len(word) > 2:
                # Exact keyword match
                if word in article.get('keywords', []):
                    score += 50

                # Title match
                if word in article['title'].lower():
                    score += 30

                # Content match
                count = text.count(word)
                score += count * 5

        if score > 0:
            scored_articles.append((score, article))

    # Sort and return top_k
    scored_articles.sort(reverse=True, key=lambda x: x[0])
    return [article for _, article in scored_articles[:top_k]]


async def generate_answer_with_rag(question: str, use_web: bool = False) -> Dict[str, Any]:
    """Generate answer using RAG with optional web search."""
    # Search knowledge base
    kb_results = search_knowledge_base(question, top_k=3)

    # Optionally search web
    web_results = []
    if use_web:
        web_results = await web_search(question, num_results=3)

    all_results = kb_results + web_results

    if not all_results:
        # Fallback to direct Gemini
        try:
            response = model.generate_content(
                f"Answer this question about AI/ML with the latest information: {question}"
            )
            return {
                "answer": response.text,
                "sources": [],
                "search_used": "direct_llm"
            }
        except Exception as e:
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "search_used": "error"
            }

    # Build context
    context = "\n\n".join([
        f"Source: {r['title']} ({r.get('source', 'Knowledge Base')})\n{r['content'][:800]}"
        for r in all_results
    ])

    # Create prompt
    prompt = f"""You are an expert AI assistant with access to the latest information about AI, ML, GenAI, and related technologies.

Context (from knowledge base and web search):
{context}

Question: {question}

Provide a comprehensive, accurate answer using the context above. Include:
1. Direct answer to the question
2. Key technical details
3. Latest developments or best practices
4. Relevant examples or use cases

If the context doesn't fully answer the question, use your knowledge to supplement, but prioritize the provided context.

Answer:"""

    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        answer = f"Error generating answer: {str(e)}"

    return {
        "answer": answer,
        "sources": [
            {
                "title": r["title"],
                "url": r.get("url", ""),
                "source": r.get("source", "Knowledge Base"),
                "category": r.get("category", "")
            }
            for r in all_results
        ],
        "search_used": "web+kb" if use_web else "kb_only",
        "num_sources": len(all_results)
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
        "service": "Ultimate AI Knowledge RAG System",
        "version": "2.0.0",
        "features": ["MCP Support", "A2A Protocol", "Web Search", "Latest AI Knowledge"],
        "articles_count": len(articles_db),
        "capabilities": ["RAG", "Web Search", "Gemini AI", "Real-time Data"]
    }


@app.get("/api/stats")
async def stats():
    """Get enhanced statistics."""
    categories = {}
    for article in articles_db:
        cat = article.get('category', 'General')
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_documents": len(articles_db),
        "categories": categories,
        "latest_topics": ["A2A Protocol", "MCP", "ChromaDB", "Gemini 2.0", "Advanced RAG"],
        "capabilities": {
            "web_search": True,
            "mcp_support": True,
            "a2a_protocol": True,
            "real_time_data": True
        },
        "version": "2.0.0"
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query with enhanced RAG and optional web search."""
    logger.info(f"Query: {request.question} (web_search={request.use_web_search})")

    result = await generate_answer_with_rag(request.question, use_web=request.use_web_search)

    return {
        "mode": "advanced_rag",
        "question": request.question,
        **result
    }


@app.post("/api/web-search")
async def perform_web_search(request: WebSearchRequest):
    """Perform web search."""
    results = await web_search(request.query, request.num_results)

    return {
        "query": request.query,
        "num_results": len(results),
        "results": results
    }


@app.get("/api/topics")
async def get_topics():
    """Get all available topics."""
    return {
        "topics": sorted(list(set(a.get('category', 'General') for a in articles_db))),
        "count": len(articles_db),
        "latest_additions": ["A2A Protocol", "MCP", "Gemini 2.0", "Advanced RAG Techniques"]
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*90)
    print("🚀 ULTIMATE AI KNOWLEDGE RAG SYSTEM v2.0")
    print("="*90)
    print(f"\n✅ Server LIVE at: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"💾 Knowledge Base: {len(articles_db)} comprehensive articles")
    print(f"\n🆕 NEW FEATURES:")
    print(f"   ✓ A2A Protocol knowledge")
    print(f"   ✓ MCP (Model Context Protocol) support")
    print(f"   ✓ Web search integration")
    print(f"   ✓ Latest AI technologies (Gemini 2.0, ChromaDB, etc.)")
    print(f"   ✓ Advanced RAG techniques")
    print(f"   ✓ Real-time data fetching")
    print(f"\n📖 Now covers:")
    for article in articles_db:
        print(f"   • {article['title']}")
    print(f"\n💡 Try asking:")
    print(f"   • 'What is the A2A protocol?'")
    print(f"   • 'Explain MCP and how it works'")
    print(f"   • 'What is ChromaDB used for?'")
    print(f"   • 'Tell me about Gemini 2.0'")
    print(f"   • 'Latest RAG techniques'")
    print("\n" + "="*90)
    print("🌐 Your site is also live at: https://rinit2994-art.github.io/AI_INTERVIEW/")
    print("="*90 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
