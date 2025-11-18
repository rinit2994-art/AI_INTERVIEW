# 🔄 Continuous Pipeline with ChromaDB

**Continuously fetch web content every 10 seconds and store in ChromaDB with semantic search**

## 🌟 Features

- ✅ **Continuous fetching** - Runs every 10 seconds (configurable)
- ✅ **Best embedding model** - sentence-transformers/all-mpnet-base-v2 (768-dim)
- ✅ **Persistent storage** - ChromaDB with local persistence
- ✅ **Multi-source scraping** - HackerNews, arXiv, GitHub, Medium, Tech blogs
- ✅ **Semantic search** - Vector similarity search
- ✅ **RAG API** - Query with LLM answer generation (Gemini)
- ✅ **Automatic deduplication** - No duplicate documents
- ✅ **Graceful shutdown** - Handle Ctrl+C cleanly

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python chromadb_manager.py  # Test ChromaDB setup
python web_scraper.py       # Test web scraping
```

---

## 🚀 Quick Start

### Option 1: Continuous Mode (Default)

Run pipeline every 10 seconds:

```bash
python continuous_pipeline.py
```

Custom interval (e.g., 30 seconds):

```bash
python continuous_pipeline.py --interval 30
```

### Option 2: Interactive Mode

```bash
python continuous_pipeline.py --interactive
```

Menu options:
1. Start pipeline (10 second interval)
2. Start pipeline (custom interval)
3. Run single iteration
4. Query ChromaDB
5. Show stats
6. Reset database

### Option 3: Run Once

Run a single iteration and exit:

```bash
python continuous_pipeline.py --once
```

### Option 4: Background Service

Run in background:

```bash
nohup python continuous_pipeline.py --interval 10 > pipeline.log 2>&1 &
```

Stop:

```bash
pkill -f continuous_pipeline.py
```

---

## 🌐 RAG API Server

Start the RAG API (separate terminal):

```bash
python rag_api.py
```

Server runs on: `http://localhost:8001`

### API Endpoints

#### 1. Health Check

```bash
curl http://localhost:8001/api/health
```

Response:
```json
{
  "status": "healthy",
  "chromadb": {
    "total_documents": 1234,
    "embedding_model": "all-mpnet-base-v2",
    "embedding_dimension": 768
  },
  "sources": {
    "hacker_news": 45,
    "arxiv": 32,
    "github": 28,
    "medium": 19
  }
}
```

#### 2. Database Statistics

```bash
curl http://localhost:8001/api/stats
```

#### 3. Semantic Search

```bash
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning transformers",
    "n_results": 5
  }'
```

Response:
```json
{
  "query": "machine learning transformers",
  "results": [
    {
      "content": "...",
      "distance": 0.234,
      "metadata": {
        "title": "...",
        "url": "...",
        "source": "arxiv"
      }
    }
  ]
}
```

#### 4. RAG Query (Search + LLM Answer)

```bash
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are transformers in machine learning?",
    "n_results": 5
  }'
```

Response:
```json
{
  "question": "What are transformers in machine learning?",
  "answer": "Transformers are a neural network architecture...",
  "sources": [
    {
      "title": "...",
      "url": "...",
      "source": "arxiv",
      "distance": 0.123
    }
  ],
  "metadata": {
    "total_sources": 5,
    "embedding_model": "all-mpnet-base-v2",
    "llm_model": "gemini-1.5-flash"
  }
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CONTINUOUS PIPELINE                        │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Web Scraper  │─────▶│  ChromaDB    │                   │
│  │              │      │  Manager     │                   │
│  │ • HackerNews │      │              │                   │
│  │ • arXiv      │      │ • all-mpnet  │                   │
│  │ • GitHub     │      │ • 768-dim    │                   │
│  │ • Medium     │      │ • Persistent │                   │
│  │ • TechBlogs  │      │              │                   │
│  └──────────────┘      └──────┬───────┘                   │
│         ▲                     │                            │
│         │                     │                            │
│         │                     ▼                            │
│    Every 10s           ┌──────────────┐                   │
│                        │  RAG API     │                   │
│                        │              │                   │
│                        │ • Search     │                   │
│                        │ • Query      │                   │
│                        │ • Gemini LLM │                   │
│                        └──────────────┘                   │
│                              │                             │
│                              ▼                             │
│                        [ HTTP API ]                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Components

### 1. ChromaDBManager (`chromadb_manager.py`)

**Purpose**: Manage ChromaDB with best embedding model

**Features**:
- Persistent storage
- sentence-transformers/all-mpnet-base-v2 embedding
- Automatic deduplication
- Semantic search
- Statistics tracking

**Methods**:
- `add_documents(documents)` - Add documents with embeddings
- `query(query_text, n_results)` - Semantic search
- `count()` - Get document count
- `get_stats()` - Get statistics
- `reset()` - Clear database

### 2. WebScraper (`web_scraper.py`)

**Purpose**: Fetch content from multiple web sources

**Sources**:
- **HackerNews** - Latest tech stories via Algolia API
- **arXiv** - Latest AI/ML papers via RSS
- **GitHub** - Trending repositories + READMEs
- **Medium** - AI/ML articles via RSS
- **TechBlogs** - AWS ML, OpenAI, Google AI blogs

**Methods**:
- `fetch_all()` - Fetch from all sources
- `fetch_hacker_news()` - HackerNews stories
- `fetch_arxiv()` - arXiv papers
- `fetch_github_trending()` - GitHub repos
- `fetch_medium_rss()` - Medium articles
- `fetch_tech_blogs()` - Tech blog posts

### 3. ContinuousPipeline (`continuous_pipeline.py`)

**Purpose**: Orchestrate continuous fetching and storage

**Features**:
- Configurable interval (default 10 seconds)
- Graceful shutdown (Ctrl+C)
- Progress tracking
- Error recovery
- Statistics logging

**Modes**:
- **Continuous** - Run forever with interval
- **Interactive** - Menu-driven interface
- **Once** - Single iteration

### 4. RAG API (`rag_api.py`)

**Purpose**: Query interface with LLM

**Features**:
- FastAPI REST API
- Semantic search endpoint
- RAG query endpoint (search + LLM)
- Health checks
- Statistics

**Stack**:
- ChromaDB for vector search
- Gemini 1.5 Flash for answer generation
- FastAPI for HTTP API

---

## 🧠 Embedding Model

**Model**: `sentence-transformers/all-mpnet-base-v2`

**Why this model?**
- ✅ State-of-the-art performance on semantic search
- ✅ 768 dimensions (high quality)
- ✅ Based on MPNet architecture
- ✅ Best balance of quality vs speed
- ✅ Open source, runs locally

**Alternatives**:
- `all-MiniLM-L6-v2` - Faster, 384-dim (good quality)
- `all-mpnet-base-v2` - Best quality, 768-dim (recommended)
- `e5-large-v2` - Very good, 1024-dim (slower)

---

## 📈 Performance

### Storage

- **Embedding size**: ~3 KB per document (768-dim)
- **1000 documents**: ~3 MB
- **10,000 documents**: ~30 MB
- **100,000 documents**: ~300 MB

### Speed

- **Embedding generation**: ~10ms per document
- **Search query**: ~50ms for 10k documents
- **Full pipeline iteration**: ~10-30 seconds (with web fetching)

### Fetching

- **Per iteration**: ~20-30 documents fetched
- **Per hour** (10s interval): ~360 iterations = ~7,200 docs
- **Per day**: ~172,800 documents (with deduplication)

---

## 🔧 Configuration

### Change Interval

```bash
# 30 seconds
python continuous_pipeline.py --interval 30

# 1 minute
python continuous_pipeline.py --interval 60

# 5 minutes
python continuous_pipeline.py --interval 300
```

### Change Storage Directory

```bash
python continuous_pipeline.py --persist-dir /path/to/chroma_db
```

### Enable/Disable Sources

Edit `web_scraper.py`:

```python
self.sources = {
    'hacker_news': {'enabled': True},
    'arxiv_ai': {'enabled': True},
    'github_trending': {'enabled': False},  # Disable GitHub
    'medium_ai': {'enabled': True}
}
```

### Change Embedding Model

Edit `chromadb_manager.py`:

```python
# Change from all-mpnet-base-v2 to all-MiniLM-L6-v2 (faster)
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # 384-dim, faster
)
```

---

## 🧪 Testing

### Test ChromaDB

```bash
python chromadb_manager.py
```

Expected output:
```
✅ Added 2 test documents
🔍 Query results:
  1. Distance: 0.2345
     Content: ChromaDB is an open-source...
📊 Stats:
  total_documents: 2
  embedding_model: all-mpnet-base-v2
```

### Test Web Scraper

```bash
python web_scraper.py
```

Expected output:
```
📰 HackerNews: 5 articles
📄 arXiv: 5 papers
⭐ GitHub: 5 repositories
✍️  Medium: 3 articles
📝 TechBlogs: 4 posts
✅ Fetched 22 documents from all sources
```

### Test Pipeline (Once)

```bash
python continuous_pipeline.py --once
```

Expected output:
```
🔄 Iteration 1 - 2024-01-15 10:30:45
🌐 Fetching from all sources...
📰 HackerNews: 5 articles
...
✅ Added 18 documents
📊 Pipeline Stats:
   Total in DB: 18
```

---

## 📝 Usage Examples

### Example 1: Start Pipeline

```bash
# Terminal 1: Start continuous pipeline
python continuous_pipeline.py --interval 10

# Let it run and collect documents...
# Press Ctrl+C to stop
```

### Example 2: Query via API

```bash
# Terminal 1: Start pipeline (if not running)
python continuous_pipeline.py --interval 10

# Terminal 2: Start RAG API
python rag_api.py

# Terminal 3: Query
curl -X POST http://localhost:8001/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest developments in AI?"}'
```

### Example 3: Interactive Mode

```bash
python continuous_pipeline.py --interactive

# Choose option 1 to start pipeline
# Choose option 4 to query
# Choose option 5 to see stats
```

---

## 🐛 Troubleshooting

### ChromaDB download error (403)

**Issue**: ChromaDB embedding model download blocked

**Solution**: Pre-download on local machine:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-mpnet-base-v2')
```

### Rate limiting from sources

**Issue**: Too many requests to web sources

**Solution**: Increase interval:
```bash
python continuous_pipeline.py --interval 30  # 30 seconds
```

### Out of memory

**Issue**: Too many documents in ChromaDB

**Solution**:
1. Reset database: Choose option 6 in interactive mode
2. Reduce fetched documents in `web_scraper.py` (change `[:5]` to `[:2]`)

### API not responding

**Issue**: RAG API won't start

**Check**:
1. ChromaDB has documents: `python continuous_pipeline.py --once`
2. Port 8001 is free: `lsof -i :8001`
3. Dependencies installed: `pip install -r requirements.txt`

---

## 🚀 Production Deployment

### Use systemd (Linux)

Create `/etc/systemd/system/continuous-pipeline.service`:

```ini
[Unit]
Description=Continuous Web Content Pipeline
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/continuous_pipeline
ExecStart=/usr/bin/python3 continuous_pipeline.py --interval 10
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable continuous-pipeline
sudo systemctl start continuous-pipeline
sudo systemctl status continuous-pipeline
```

### Use Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "continuous_pipeline.py", "--interval", "10"]
```

Build and run:
```bash
docker build -t continuous-pipeline .
docker run -d -v ./chroma_db:/app/chroma_db continuous-pipeline
```

---

## 📚 File Structure

```
continuous_pipeline/
├── chromadb_manager.py      # ChromaDB with embeddings
├── web_scraper.py            # Multi-source scraping
├── continuous_pipeline.py    # Main orchestrator
├── rag_api.py                # FastAPI server
├── requirements.txt          # Dependencies
├── README.md                 # This file
└── chroma_db/                # Persistent storage (auto-created)
```

---

## 🎯 Key Metrics

After running for 1 hour (10s interval):

```
📊 Stats:
   Total iterations: 360
   Total documents added: ~5,000-7,000
   Unique documents: ~2,000-3,000 (after deduplication)
   Sources:
     - hacker_news: ~800
     - arxiv: ~600
     - github: ~400
     - medium: ~300
     - tech_blog: ~200
```

---

## 🔗 References

- **ChromaDB**: https://www.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **all-mpnet-base-v2**: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
- **FastAPI**: https://fastapi.tiangolo.com/
- **Gemini API**: https://ai.google.dev/

---

## 📄 License

MIT License - See LICENSE file

---

**Built with ❤️ for continuous knowledge base expansion**
