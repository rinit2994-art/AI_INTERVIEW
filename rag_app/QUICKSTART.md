# 🚀 Quick Start Guide

Get the AI Knowledge RAG System up and running in 5 minutes!

## 📋 Prerequisites

- Python 3.11 or higher
- Git
- Gemini API Key ([Get one FREE here](https://makersuite.google.com/app/apikey))

## 🎯 Fast Setup (3 Steps)

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd rag_app

# Copy environment template
cp .env.example .env
```

### Step 2: Add Your API Key

Edit `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Run!

#### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

#### Windows:
```cmd
start.bat
```

#### Or manually:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access the App

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🎮 First Steps

### 1. Fetch Articles

Click "🔄 Fetch New Articles" in the sidebar to populate the knowledge base with:
- Latest AI/ML articles from Medium
- Recent papers from arXiv
- Towards Data Science posts
- Google AI Blog updates

This will take 2-5 minutes depending on network speed.

### 2. Ask Questions

Try these example questions:

- "What is retrieval augmented generation?"
- "Explain how transformers work"
- "What are the latest developments in generative AI?"
- "How do I implement a neural network in Python?"

### 3. Switch Modes

Try different query modes:

- **Answer Mode** (default): Get detailed answers with citations
- **Search Mode**: Find relevant documents without generating an answer
- **Auto Mode**: Let the AI agent decide the best approach

## 🐳 Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔍 Verify Installation

### Check Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Knowledge RAG System",
  "version": "1.0.0"
}
```

### Check Stats
```bash
curl http://localhost:8000/api/stats
```

### Test Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "mode": "answer"
  }'
```

## 🎨 UI Overview

```
┌─────────────────────────────────────────────────┐
│  🤖 AI Knowledge RAG System                     │
│  Powered by Google ADK, LangChain & Gemini AI   │
├─────────────────────────────────────────────────┤
│  Chat Interface         │  Sidebar              │
│                         │  ┌──────────────────┐ │
│  [Your questions here]  │  │ 📊 Stats         │ │
│                         │  │ Total: 0 docs    │ │
│  [AI responses with     │  └──────────────────┘ │
│   citations]            │  ┌──────────────────┐ │
│                         │  │ ⚙️  Actions      │ │
│  [Mode: Answer ▼]       │  │ 🔄 Fetch         │ │
│                         │  │ 📈 Refresh       │ │
│  [Type your question]   │  │ 🗑️  Clear        │ │
│  [Send]                 │  └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not set"
- Make sure you edited `.env` and added your API key
- Restart the server after editing `.env`

### Error: "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Make sure virtual environment is activated

### Error: "Port 8000 already in use"
- Stop any other service using port 8000
- Or change the port: `uvicorn backend.api.main:app --port 8001`

### No articles fetched
- Check your internet connection
- Some sources might be temporarily unavailable
- Try fetching again after a few minutes

### Slow responses
- First query after startup is slower (model loading)
- Subsequent queries should be faster
- Consider using a smaller embedding model

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the full README**: Check [README.md](README.md)
3. **Customize sources**: Edit `config/settings.py`
4. **Add more sources**: Extend `backend/services/article_fetcher.py`
5. **Deploy**: Follow the deployment guide in README

## 💡 Pro Tips

- Fetch articles regularly to keep knowledge base updated
- Use "Search Mode" to explore available content
- "Auto Mode" lets ADK agents choose the best strategy
- Check stats regularly to monitor knowledge base growth
- Clear database and re-fetch for fresh content

## 🆘 Need Help?

- Check the full [README.md](README.md)
- Visit the API docs at `/docs`
- Open an issue on GitHub
- Check logs for error messages

---

**Happy exploring! 🚀**
