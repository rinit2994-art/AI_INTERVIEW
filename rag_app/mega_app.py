"""
MEGA RAG Application - 4,194 Knowledge Entries!
Full-powered RAG with your entire TypeScript knowledge base.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

# Import the knowledge base manager
from knowledge_base_manager_v2 import KnowledgeBaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MEGA RAG - 4,194 Knowledge Entries",
    description="Ultimate AI Knowledge RAG System with your full TypeScript knowledge base",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Knowledge Base Manager
logger.info("🚀 Initializing MEGA Knowledge Base...")
kb_manager = KnowledgeBaseManager()
kb_manager.parse_typescript_kb()
kb_manager.build_indexes()
logger.info(f"✅ Loaded {len(kb_manager.entries)} knowledge entries!")

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
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
        <title>MEGA RAG - 4,194 Knowledge Entries</title>
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
                max-width: 1000px;
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

            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}

            .stats-bar {{
                background: rgba(255,255,255,0.2);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                color: white;
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }}

            .stat-item {{
                text-align: center;
                padding: 10px;
            }}

            .stat-value {{
                font-size: 2em;
                font-weight: bold;
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
                height: 500px;
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
                background: #667eea;
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
                max-width: 90%;
            }}

            .sources {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }}

            .source-item {{
                background: #f0f0f0;
                padding: 10px;
                margin: 8px 0;
                border-radius: 8px;
                font-size: 0.9em;
            }}

            .source-title {{
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }}

            .source-keywords {{
                color: #666;
                font-size: 0.85em;
                margin-top: 5px;
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

            button:active {{
                transform: translateY(0);
            }}

            button:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
            }}

            .loading {{
                text-align: center;
                padding: 20px;
                color: #666;
            }}

            .category-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }}

            .category-tag {{
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.8em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 MEGA RAG System</h1>
                <p>Your Complete AI Knowledge Base - Ask Anything!</p>
            </div>

            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{stats['total_entries']:,}</div>
                    <div class="stat-label">Knowledge Entries</div>
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
                    <div class="stat-value">{stats['avg_keywords_per_entry']}</div>
                    <div class="stat-label">Avg Keywords/Entry</div>
                </div>
            </div>

            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message">
                        <div class="ai-message">
                            <strong>Welcome to MEGA RAG!</strong><br><br>
                            I have access to <strong>{stats['total_entries']:,} knowledge entries</strong> covering:<br><br>
                            <div class="category-tags">
                                {"".join([f'<span class="category-tag">{cat}: {count}</span>' for cat, count in stats['category_breakdown'].items()])}
                            </div>
                            <br><br>
                            Ask me anything about AI, ML, Data Science, GenAI, Google ADK, Transformers, and more!
                        </div>
                    </div>
                </div>

                <div class="input-area">
                    <input
                        type="text"
                        id="questionInput"
                        placeholder="Ask a question about AI, ML, Data Science..."
                        onkeypress="if(event.key === 'Enter') askQuestion()"
                    >
                    <button onclick="askQuestion()" id="askButton">Ask</button>
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
                loadingMsg.innerHTML = '<div class="ai-message loading">Searching {stats['total_entries']:,} entries...</div>';
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
                        sourcesHTML = '<div class="sources"><strong>📚 Sources:</strong>';
                        data.sources.forEach(source => {{
                            const keywords = source.keywords ? source.keywords.slice(0, 5).join(', ') : '';
                            sourcesHTML += `
                                <div class="source-item">
                                    <div class="source-title">${{source.title}}</div>
                                    <div>${{source.content.substring(0, 200)}}...</div>
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
                                Searched ${{data.total_entries_searched.toLocaleString()}} entries
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
    """Query the knowledge base."""
    try:
        logger.info(f"Query: {request.question}")

        # Search knowledge base
        results = kb_manager.search(request.question, top_k=request.top_k)

        if not results:
            return QueryResponse(
                answer="I couldn't find any information about that topic in my knowledge base. Try asking about AI, Machine Learning, Deep Learning, GenAI, Google ADK, or related topics.",
                sources=[],
                total_entries_searched=len(kb_manager.entries),
                stats=kb_manager.get_stats()
            )

        # Build comprehensive answer from top results
        answer_parts = []
        for i, result in enumerate(results, 1):
            answer_parts.append(f"**{result['title']}**\n\n{result['content']}\n")

        answer = "\n---\n\n".join(answer_parts)

        # Get stats
        stats = kb_manager.get_stats()

        return QueryResponse(
            answer=answer,
            sources=results,
            total_entries_searched=len(kb_manager.entries),
            stats=stats
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    return kb_manager.get_stats()


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "total_entries": len(kb_manager.entries),
        "total_keywords": len(kb_manager.keyword_index),
        "categories": len(kb_manager.categories)
    }


@app.get("/api/categories")
async def get_categories():
    """Get all categories and their entry counts."""
    stats = kb_manager.get_stats()
    return stats['category_breakdown']


@app.get("/api/top-keywords")
async def get_top_keywords(limit: int = 20):
    """Get top keywords by frequency."""
    stats = kb_manager.get_stats()
    return stats['top_keywords'][:limit]


@app.get("/api/search/{query}")
async def search(query: str, top_k: int = 5):
    """Simple search endpoint."""
    results = kb_manager.search(query, top_k=top_k)
    return {
        "query": query,
        "results": results,
        "total_found": len(results)
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 MEGA RAG APPLICATION - STARTING")
    print("="*80)
    print(f"\n📊 Knowledge Base Stats:")
    stats = kb_manager.get_stats()
    print(f"   Total Entries: {stats['total_entries']:,}")
    print(f"   Unique Keywords: {stats['total_unique_keywords']:,}")
    print(f"   Categories: {stats['total_categories']}")
    print(f"   Avg Keywords/Entry: {stats['avg_keywords_per_entry']}")
    print(f"\n📂 Categories:")
    for cat, count in stats['category_breakdown'].items():
        print(f"   {cat}: {count:,} entries")
    print(f"\n🔥 Top 5 Keywords:")
    for kw, count in stats['top_keywords'][:5]:
        print(f"   {kw}: {count:,} entries")
    print("\n" + "="*80)
    print("🌐 Starting server on http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
