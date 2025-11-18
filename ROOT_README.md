# 🚀 AI Interview Projects Suite

This repository contains **TWO distinct AI-powered applications** for interview preparation and knowledge management:

## 📦 Projects Overview

### 1. 🎯 Instant Mock Interview System (TypeScript)
**Location:** `src/` directory
**Tech Stack:** TypeScript, Express, Node.js, MCP SDK

An instant mock interview system with **hardcoded answers** for common technical interview questions. No API calls, no delays - just immediate, comprehensive answers!

**Features:**
- ⚡ **Instant Responses** - All 50+ Q&A pairs are hardcoded
- 🌐 **Multiple Interfaces** - CLI, Web UI, and MCP Server
- 📚 **Comprehensive Coverage** - JavaScript, React, Node.js, Data Structures, Algorithms, System Design, etc.
- 💾 **Zero External Dependencies** - Works completely offline
- 🔥 **Firebase Integration** - Optional persistence

**Quick Start:**
```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run Web Server (http://localhost:3000)
npm start

# Or run CLI interface
npm run cli
```

[📖 Full Documentation](./README.md)

---

### 2. 🤖 AI Knowledge RAG System (Python)
**Location:** `rag_app/` directory
**Tech Stack:** Python, FastAPI, Google ADK, LangChain, ChromaDB, Gemini AI

An intelligent **Retrieval Augmented Generation (RAG)** system that automatically fetches, processes, and indexes AI/ML articles from multiple sources, providing an agentic search and question-answering interface.

**Features:**
- 🧠 **Agentic AI** - Powered by Google ADK with specialized agents
- 🔍 **Smart RAG Pipeline** - LangChain + ChromaDB for semantic search
- 📚 **Multi-Source Fetching** - Medium, arXiv, Towards Data Science, Google AI Blog
- ⚡ **Real-time Chat Interface** - Modern web UI with multiple query modes
- 🚀 **Docker Support** - Easy deployment with Docker Compose
- 🎯 **Three Query Modes** - Answer, Search, and Auto mode

**Quick Start:**
```bash
cd rag_app

# Install Python dependencies
pip install -r requirements.txt

# Configure environment (add your Gemini API key)
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Run the application
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Or use Docker
docker-compose up -d
```

[📖 Full Documentation](./rag_app/README.md)

---

## 🎓 Which Project Should You Use?

| Use Case | Recommended Project |
|----------|-------------------|
| Quick interview prep (offline) | 🎯 Mock Interview System |
| Practice common technical questions | 🎯 Mock Interview System |
| Deep dive into AI/ML topics | 🤖 RAG System |
| Research latest AI trends | 🤖 RAG System |
| No internet connectivity | 🎯 Mock Interview System |
| Advanced semantic search | 🤖 RAG System |

---

## 📁 Repository Structure

```
AI_INTERVIEW/
├── src/                              # TypeScript Mock Interview System
│   ├── cli.ts                        # CLI interface
│   ├── web-server.ts                 # Express web server
│   ├── mcp-server.ts                 # MCP server implementation
│   ├── interview-database.ts         # Hardcoded Q&A database
│   └── instant-interview-handler.ts  # Answer matching logic
│
├── rag_app/                          # Python RAG System
│   ├── backend/
│   │   ├── agents/                   # Google ADK agents
│   │   ├── api/                      # FastAPI application
│   │   └── services/                 # Core services
│   ├── config/                       # Configuration
│   ├── frontend/                     # Web UI
│   └── vector_db/                    # ChromaDB persistence
│
├── dist/                             # Compiled TypeScript (generated)
├── node_modules/                     # NPM dependencies (generated)
├── package.json                      # NPM configuration
├── tsconfig.json                     # TypeScript configuration
├── README.md                         # Mock Interview docs
└── ROOT_README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

**For Mock Interview System:**
- Node.js 18.0+
- npm

**For RAG System:**
- Python 3.11+
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))
- Docker (optional)

### Installation Steps

#### Both Projects:
```bash
# Clone the repository
git clone <repository-url>
cd AI_INTERVIEW
```

#### Mock Interview System Only:
```bash
npm install
npm run build
npm start
```

#### RAG System Only:
```bash
cd rag_app
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
python -m uvicorn backend.api.main:app --reload
```

---

## 💡 Usage Examples

### Mock Interview System

**Web Interface:**
1. Start server: `npm start`
2. Open: http://localhost:3000
3. Ask: "What is closure in JavaScript?"
4. Get instant answer!

**CLI:**
```bash
npm run cli
# Type: What is the event loop in JavaScript?
# Or: random  # Get a random question
# Or: categories  # See all topics
```

### RAG System

**Web Interface:**
1. Start server: `python -m uvicorn backend.api.main:app --reload`
2. Open: http://localhost:8000
3. Select mode: Answer/Search/Auto
4. Ask: "Explain transformer architecture in detail"
5. Get answer with citations!

**API:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "mode": "answer"}'
```

---

## 🛠️ Development

### TypeScript Development
```bash
npm run dev          # Run web server with auto-reload
npm run dev:cli      # Run CLI with auto-reload
npm run build        # Compile TypeScript
```

### Python Development
```bash
cd rag_app
python -m pytest                    # Run tests
black .                             # Format code
python -m uvicorn backend.api.main:app --reload  # Dev server
```

---

## 📊 Technology Stack Comparison

| Feature | Mock Interview | RAG System |
|---------|---------------|------------|
| **Language** | TypeScript | Python |
| **Web Framework** | Express | FastAPI |
| **AI/LLM** | None (hardcoded) | Gemini AI |
| **Vector DB** | None | ChromaDB |
| **Agents** | None | Google ADK |
| **Embedding** | None | HuggingFace |
| **Data Source** | Static | Dynamic (web scraping) |
| **Offline Support** | ✅ Yes | ❌ No |
| **API Keys Required** | ❌ No | ✅ Yes (Gemini) |

---

## 🔐 Security Notes

### Mock Interview System
- No API keys required
- No sensitive data
- Can run completely offline

### RAG System
- **IMPORTANT:** Never commit `.env` file with API keys
- Store `GEMINI_API_KEY` securely
- Use environment variables in production
- Implement rate limiting for public deployment
- Add authentication for API endpoints

---

## 📝 License

Apache-2.0 License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📧 Support

For issues or questions:
- Check project-specific READMEs
- Open an issue on GitHub
- Review API documentation

---

## 🎯 Quick Links

- [Mock Interview Documentation](./README.md)
- [RAG System Documentation](./rag_app/README.md)
- [TypeScript Source](./src/)
- [Python Source](./rag_app/backend/)
- [Get Gemini API Key](https://makersuite.google.com/app/apikey)

---

**Built with ❤️ for Interview Success and Knowledge Discovery**
