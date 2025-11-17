# 🤖 AI Knowledge RAG System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.4-orange.svg)](https://python.langchain.com/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-0.1.0-red.svg)](https://github.com/google/adk-python)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

An intelligent **Retrieval Augmented Generation (RAG)** system powered by **Google ADK** (Agent Development Kit), **LangChain**, and **Gemini AI**. This system automatically fetches, processes, and indexes articles about AI, Machine Learning, Data Science, and Generative AI from multiple sources, providing an agentic search and question-answering interface.

## ✨ Key Features

- 🧠 **Agentic AI**: Powered by Google ADK with specialized agents for search and answering
- 🔍 **Smart RAG Pipeline**: Uses LangChain for document processing and retrieval
- 📚 **Multi-Source Fetching**: Automatically pulls content from:
  - Medium (AI/ML tags)
  - arXiv (cs.AI, cs.LG, cs.CL)
  - Towards Data Science
  - Google AI Blog
- 🗃️ **Vector Database**: ChromaDB for efficient semantic search
- ⚡ **Real-time Chat Interface**: Modern web UI with multiple query modes
- 🚀 **Docker Support**: Easy deployment with Docker Compose
- 🔄 **Background Processing**: Async article fetching and indexing
- 🎯 **Three Query Modes**:
  - **Answer Mode**: Get detailed answers with citations (RAG)
  - **Search Mode**: Find relevant documents
  - **Auto Mode**: Let ADK agents decide the best approach

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (HTML/JS)                     │
│                  Modern Chat Interface                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  ADK Agents  │  │ RAG Pipeline │  │Article Fetcher│      │
│  │              │  │              │  │               │      │
│  │ • Coordinator│  │ • LangChain  │  │ • Medium      │      │
│  │ • Search     │  │ • Gemini AI  │  │ • arXiv       │      │
│  │ • Answer     │  │ • Retrieval  │  │ • TDS         │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘      │
│         │                  │                  │               │
└─────────┼──────────────────┼──────────────────┼───────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    ChromaDB Vector Store                     │
│          (Embeddings: all-MiniLM-L6-v2)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

#### Method 1: Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag_app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

5. **Run the application**
```bash
# Start the server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Method 2: Docker (Recommended)

1. **Clone and configure**
```bash
git clone <repository-url>
cd rag_app
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

2. **Build and run**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Select a query mode (Answer/Search/Auto)
3. Ask questions about AI, ML, or Data Science
4. View answers with source citations

### Fetch New Articles

Click the "🔄 Fetch New Articles" button in the sidebar to:
- Scrape latest content from configured sources
- Process and chunk documents
- Add embeddings to vector database

### API Endpoints

#### Health Check
```bash
GET /api/health
```

#### Get Statistics
```bash
GET /api/stats
```

#### Query the Knowledge Base
```bash
POST /api/query
Content-Type: application/json

{
  "question": "What is retrieval augmented generation?",
  "mode": "answer",  # "search", "answer", or "auto"
  "top_k": 5
}
```

#### Fetch New Articles
```bash
POST /api/fetch-articles
Content-Type: application/json

{
  "force": false
}
```

#### Clear Database
```bash
DELETE /api/clear
```

## 🔧 Configuration

Edit `config/settings.py` or set environment variables in `.env`:

```env
# Gemini API
GEMINI_API_KEY=your_key_here

# Vector Database
CHROMA_PERSIST_DIRECTORY=./vector_db/chroma_data
COLLECTION_NAME=ai_knowledge_base

# Scraping
MAX_ARTICLES_PER_SOURCE=50
FETCH_INTERVAL_HOURS=24

# Sources
MEDIUM_TAGS=artificial-intelligence,machine-learning,data-science,generative-ai,llm
ARXIV_CATEGORIES=cs.AI,cs.LG,cs.CL
```

## 🧩 Project Structure

```
rag_app/
├── backend/
│   ├── agents/
│   │   └── adk_agents.py          # Google ADK agent implementation
│   ├── api/
│   │   └── main.py                # FastAPI application
│   └── services/
│       ├── article_fetcher.py     # Multi-source content fetcher
│       ├── vector_store.py        # ChromaDB vector database
│       └── rag_pipeline.py        # LangChain RAG pipeline
├── config/
│   └── settings.py                # Application configuration
├── frontend/
│   └── index.html                 # Web interface
├── vector_db/                     # ChromaDB persistence
├── data/                          # Cached articles
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose setup
└── README.md                      # This file
```

## 🤖 Google ADK Agents

The system uses three specialized ADK agents:

1. **Coordinator Agent**: Main orchestrator that routes queries
2. **Search Agent**: Specialized in finding relevant documents
3. **Answer Agent**: Generates comprehensive answers using RAG

### Agent Workflow

```
User Query
    ↓
Coordinator Agent (decides best approach)
    ↓
    ├─→ Search Agent → Vector Search → Results
    │
    └─→ Answer Agent → RAG Pipeline → Gemini → Answer + Citations
```

## 📊 Data Sources

### Currently Supported

- **Medium**: AI, ML, Data Science, Generative AI, LLM, Deep Learning, NLP tags
- **arXiv**: cs.AI, cs.LG, cs.CL categories
- **Towards Data Science**: Latest articles
- **Google AI Blog**: Research updates

### Adding New Sources

Extend `backend/services/article_fetcher.py` with new fetch methods:

```python
async def fetch_new_source(self, params) -> List[Dict[str, Any]]:
    # Implement fetching logic
    return articles
```

## 🔍 RAG Pipeline Details

### Document Processing

1. **Fetch**: Articles from multiple sources
2. **Extract**: Clean text extraction using trafilatura
3. **Chunk**: Recursive text splitting (1000 chars, 200 overlap)
4. **Embed**: HuggingFace embeddings (all-MiniLM-L6-v2)
5. **Store**: ChromaDB vector database

### Query Processing

1. **User Query** → Embedding
2. **Similarity Search** → Top-k relevant chunks
3. **Context Assembly** → Format retrieved documents
4. **LLM Generation** → Gemini produces answer
5. **Citation Addition** → Add source metadata

## 🚢 Deployment

### Docker Deployment

```bash
# Build
docker build -t ai-rag-system .

# Run
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/vector_db:/app/vector_db \
  ai-rag-system
```

### Cloud Deployment Options

- **Google Cloud Run**: Deploy containerized app
- **AWS ECS/Fargate**: Container orchestration
- **Azure Container Instances**: Serverless containers
- **Kubernetes**: Full orchestration with scaling

## 🧪 Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/
```

## 🔐 Security Notes

- Store `GEMINI_API_KEY` securely (use secrets management)
- Don't commit `.env` file to version control
- Implement rate limiting for production
- Add authentication for API endpoints
- Sanitize user inputs
- Use HTTPS in production

## 📈 Performance Optimization

- **Caching**: Implement Redis for query caching
- **Batch Processing**: Process multiple articles concurrently
- **Index Optimization**: Tune ChromaDB parameters
- **Model Selection**: Choose appropriate Gemini model for use case
- **Load Balancing**: Deploy multiple instances with load balancer

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google ADK](https://github.com/google/adk-python) - Agent Development Kit
- [LangChain](https://python.langchain.com/) - RAG framework
- [Gemini AI](https://ai.google.dev/) - Language model
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

## 🗺️ Roadmap

- [ ] Add more data sources (Reddit, Twitter, etc.)
- [ ] Implement user authentication
- [ ] Add query history and bookmarks
- [ ] Support for PDF/document upload
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] GraphQL API option
- [ ] Real-time updates via WebSocket
- [ ] Mobile app

---

Built with ❤️ using Google ADK, LangChain, and Gemini AI
