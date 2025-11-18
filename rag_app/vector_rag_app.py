"""
Vector RAG Application with ChromaDB
Proper semantic search using embeddings and vector similarity
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import chromadb
from chromadb.config import Settings
import json

# Import knowledge base manager
from knowledge_base_manager_v2 import KnowledgeBaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Vector RAG - Semantic Search with ChromaDB",
    description="True RAG with vector embeddings and semantic similarity",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB with default embedding function
logger.info("🔧 Initializing ChromaDB with built-in embeddings...")
chroma_client = chromadb.Client(Settings(
    anonymized_telemetry=False,
    allow_reset=True
))

# Create or get collection with default embedding function
collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"description": "AI/ML Knowledge Base with 4,194 entries"}
)

logger.info("✅ ChromaDB initialized with default embedding function!")
embedding_model = None  # Using ChromaDB's built-in embeddings

# Load knowledge base
logger.info("📚 Loading knowledge base...")
kb_manager = KnowledgeBaseManager()
kb_manager.parse_typescript_kb()
kb_manager.build_indexes()
logger.info(f"✅ Loaded {len(kb_manager.entries)} knowledge entries!")

# Check if collection is empty and populate
if collection.count() == 0:
    logger.info("🔄 Populating ChromaDB with embeddings...")
    logger.info("This will take a few minutes for 4,194 entries...")

    # Process in batches for efficiency
    batch_size = 100
    total_entries = len(kb_manager.entries)

    for i in range(0, total_entries, batch_size):
        batch = kb_manager.entries[i:i+batch_size]

        # Prepare batch data
        documents = []
        metadatas = []
        ids = []

        for j, entry in enumerate(batch):
            # Combine title and content for embedding
            text = f"{entry['title']}\n\n{entry['content']}"
            documents.append(text)

            # Metadata
            metadatas.append({
                'title': entry['title'],
                'category': entry.get('category', 'General'),
                'keywords': ','.join(entry.get('keywords', [])[:10])  # First 10 keywords
            })

            # Unique ID
            ids.append(f"doc_{i+j}")

        # Add to ChromaDB (ChromaDB will generate embeddings automatically)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"   Processed {min(i+batch_size, total_entries)}/{total_entries} entries...")

    logger.info(f"✅ ChromaDB populated with {collection.count()} entries!")
else:
    logger.info(f"✅ ChromaDB already populated with {collection.count()} entries!")


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    similarity_scores: List[float]
    total_entries_searched: int
    stats: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend."""
    stats = kb_manager.get_stats()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vector RAG - Semantic Search with ChromaDB</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}

            .header {{
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }}

            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}

            .header .subtitle {{
                font-size: 1.2em;
                opacity: 0.95;
                margin-bottom: 10px;
            }}

            .tech-badge {{
                display: inline-block;
                background: rgba(255,255,255,0.3);
                padding: 8px 16px;
                border-radius: 20px;
                margin: 5px;
                font-size: 0.9em;
            }}

            .stats-bar {{
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                color: white;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }}

            .stat-item {{
                text-align: center;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }}

            .stat-value {{
                font-size: 2.2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}

            .stat-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}

            .chat-container {{
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}

            .chat-messages {{
                height: 550px;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }}

            .message {{
                margin-bottom: 20px;
                animation: fadeIn 0.3s;
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            .user-message {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 18px;
                border-radius: 18px;
                max-width: 80%;
                margin-left: auto;
                text-align: right;
            }}

            .ai-message {{
                background: white;
                padding: 15px 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                max-width: 95%;
            }}

            .similarity-score {{
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                margin-left: 10px;
            }}

            .sources {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }}

            .source-item {{
                background: #f0f0f0;
                padding: 12px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 3px solid #667eea;
            }}

            .source-title {{
                font-weight: bold;
                color: #667eea;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}

            .source-category {{
                background: #667eea;
                color: white;
                padding: 3px 10px;
                border-radius: 10px;
                font-size: 0.8em;
            }}

            .source-content {{
                color: #333;
                margin: 8px 0;
                line-height: 1.5;
            }}

            .source-keywords {{
                color: #666;
                font-size: 0.85em;
                margin-top: 8px;
            }}

            .input-area {{
                display: flex;
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
            }}

            input {{
                flex: 1;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }}

            input:focus {{
                border-color: #667eea;
            }}

            button {{
                margin-left: 10px;
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}

            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}

            button:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }}

            .loading {{
                text-align: center;
                padding: 20px;
                color: #666;
            }}

            .vector-icon {{
                font-size: 1.2em;
                margin-right: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Vector RAG System</h1>
                <p class="subtitle">Semantic Search with ChromaDB & Embeddings</p>
                <div>
                    <span class="tech-badge">🔮 ChromaDB</span>
                    <span class="tech-badge">🎯 Sentence Transformers</span>
                    <span class="tech-badge">📊 {stats['total_entries']:,} Entries</span>
                    <span class="tech-badge">🔍 Vector Similarity</span>
                </div>
            </div>

            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{collection.count():,}</div>
                    <div class="stat-label">Vectorized Entries</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats['total_unique_keywords']:,}</div>
                    <div class="stat-label">Unique Keywords</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats['total_categories']}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">🔮</div>
                    <div class="stat-label">ChromaDB Embeddings</div>
                </div>
            </div>

            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message">
                        <div class="ai-message">
                            <strong>🚀 Welcome to Vector RAG!</strong><br><br>
                            I use <strong>semantic vector search</strong> with ChromaDB and embeddings to find the most relevant answers.<br><br>
                            <strong>What's different?</strong><br>
                            • Understands meaning, not just keywords<br>
                            • Cosine similarity scoring<br>
                            • {collection.count():,} entries with vector embeddings<br>
                            • Powered by ChromaDB's default embedding function<br><br>
                            Ask me anything about AI, ML, GenAI, Google ADK, and more!
                        </div>
                    </div>
                </div>

                <div class="input-area">
                    <input
                        type="text"
                        id="questionInput"
                        placeholder="Ask a semantic question..."
                        onkeypress="if(event.key === 'Enter') askQuestion()"
                    >
                    <button onclick="askQuestion()" id="askButton">🔍 Search</button>
                </div>
            </div>
        </div>

        <script>
            async function askQuestion() {{
                const input = document.getElementById('questionInput');
                const question = input.value.trim();

                if (!question) return;

                const messagesDiv = document.getElementById('chatMessages');
                const askButton = document.getElementById('askButton');

                // Add user message
                const userMsg = document.createElement('div');
                userMsg.className = 'message';
                userMsg.innerHTML = `<div class="user-message">${{question}}</div>`;
                messagesDiv.appendChild(userMsg);

                // Clear input
                input.value = '';

                // Show loading
                const loadingMsg = document.createElement('div');
                loadingMsg.className = 'message';
                loadingMsg.innerHTML = '<div class="ai-message loading">🔮 Computing embeddings and searching vector space...</div>';
                messagesDiv.appendChild(loadingMsg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                // Disable button
                askButton.disabled = true;

                try {{
                    const response = await fetch('/api/query', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ question: question }})
                    }});

                    const data = await response.json();

                    // Remove loading
                    messagesDiv.removeChild(loadingMsg);

                    // Add AI response
                    const aiMsg = document.createElement('div');
                    aiMsg.className = 'message';

                    let sourcesHTML = '';
                    if (data.sources && data.sources.length > 0) {{
                        sourcesHTML = '<div class="sources"><strong>📚 Most Similar Vectors:</strong>';
                        data.sources.forEach((source, idx) => {{
                            const similarity = data.similarity_scores[idx];
                            const similarityPercent = (similarity * 100).toFixed(1);
                            const keywords = source.keywords ? source.keywords.split(',').slice(0, 5).join(', ') : '';

                            sourcesHTML += `
                                <div class="source-item">
                                    <div class="source-title">
                                        <span class="vector-icon">🎯</span> ${{source.title}}
                                        <span class="similarity-score">${{similarityPercent}}% similar</span>
                                    </div>
                                    <span class="source-category">${{source.category}}</span>
                                    <div class="source-content">${{source.content.substring(0, 300)}}...</div>
                                    ${{keywords ? `<div class="source-keywords">🏷️ ${{keywords}}</div>` : ''}}
                                </div>
                            `;
                        }});
                        sourcesHTML += '</div>';
                    }}

                    aiMsg.innerHTML = `
                        <div class="ai-message">
                            ${{data.answer}}
                            ${{sourcesHTML}}
                            <div style="margin-top: 10px; font-size: 0.85em; color: #666;">
                                🔍 Searched ${{data.total_entries_searched.toLocaleString()}} vectors using cosine similarity
                            </div>
                        </div>
                    `;
                    messagesDiv.appendChild(aiMsg);

                }} catch (error) {{
                    messagesDiv.removeChild(loadingMsg);
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'message';
                    errorMsg.innerHTML = '<div class="ai-message" style="color: red;">Error: ' + error.message + '</div>';
                    messagesDiv.appendChild(errorMsg);
                }} finally {{
                    askButton.disabled = false;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query using semantic vector search."""
    try:
        logger.info(f"Vector search query: {request.question}")

        # Search in ChromaDB (it will generate embeddings automatically)
        results = collection.query(
            query_texts=[request.question],
            n_results=request.top_k
        )

        if not results['documents'][0]:
            return QueryResponse(
                answer="I couldn't find relevant information. Try asking about AI, ML, GenAI, or Google ADK.",
                sources=[],
                similarity_scores=[],
                total_entries_searched=collection.count(),
                stats=kb_manager.get_stats()
            )

        # Build response
        sources = []
        for i in range(len(results['documents'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]

            # Extract title and content from document
            parts = document.split('\n\n', 1)
            title = parts[0] if len(parts) > 0 else metadata.get('title', 'Unknown')
            content = parts[1] if len(parts) > 1 else document

            sources.append({
                'title': metadata.get('title', title),
                'content': content,
                'category': metadata.get('category', 'General'),
                'keywords': metadata.get('keywords', '')
            })

        # Get similarity scores (distances)
        distances = results['distances'][0]
        # Convert distances to similarity scores (1 - distance for cosine)
        similarity_scores = [1 - d for d in distances]

        # Build answer from top results
        answer_parts = []
        for i, source in enumerate(sources):
            similarity_percent = similarity_scores[i] * 100
            answer_parts.append(
                f"**{source['title']}** (Similarity: {similarity_percent:.1f}%)\n\n{source['content']}\n"
            )

        answer = "\n---\n\n".join(answer_parts)

        return QueryResponse(
            answer=answer,
            sources=sources,
            similarity_scores=similarity_scores,
            total_entries_searched=collection.count(),
            stats=kb_manager.get_stats()
        )

    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get statistics."""
    stats = kb_manager.get_stats()
    stats['chroma_entries'] = collection.count()
    stats['embedding_function'] = 'ChromaDB Default'
    return stats


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "total_entries": len(kb_manager.entries),
        "chroma_entries": collection.count(),
        "embedding_function": "ChromaDB Default"
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 VECTOR RAG APPLICATION - STARTING")
    print("="*80)
    print(f"\n📊 Knowledge Base Stats:")
    stats = kb_manager.get_stats()
    print(f"   Total Entries: {stats['total_entries']:,}")
    print(f"   ChromaDB Entries: {collection.count():,}")
    print(f"   Embedding Function: ChromaDB Default")
    print("\n" + "="*80)
    print("🌐 Starting server on http://localhost:8000")
    print("📖 Semantic vector search powered by ChromaDB!")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
