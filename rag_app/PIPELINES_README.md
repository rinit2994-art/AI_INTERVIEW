# 🚀 Knowledge Base Expansion Pipelines

## 📁 Available Pipelines

This directory contains **4 different pipelines** for expanding your knowledge base, each with different strengths:

---

## 🌟 1. Ultimate ADK LangChain Pipeline ⭐ **RECOMMENDED**

**File:** `ultimate_adk_langchain_pipeline.py`

**Why This Is THE BEST:**
- ✅ Google ADK's `google_search` tool (highest quality search)
- ✅ LangChain WebBaseLoader (most robust scraping)
- ✅ LangChain RecursiveCharacterTextSplitter (optimal chunking)
- ✅ ChromaDB with vector embeddings
- ✅ Parallel processing (5 workers)
- ✅ Smart deduplication

**Quality:** ⭐⭐⭐⭐⭐ (10/10)
**Speed:** ⚡⚡⚡⚡ (Fast - parallel)
**Setup:** Medium (requires Google ADK + LangChain)

**Use When:**
- You want the BEST results
- You have internet access
- You want highest quality sources

**Run:**
```bash
python ultimate_adk_langchain_pipeline.py
```

---

## 🔍 2. LangChain Google Pipeline

**File:** `langchain_google_pipeline.py`

**Features:**
- ✅ Google Custom Search API (good quality)
- ✅ LangChain WebBaseLoader (robust scraping)
- ✅ LangChain RecursiveCharacterTextSplitter (optimal chunking)
- ✅ ChromaDB with vector embeddings
- ✅ Parallel processing (5 workers)
- ✅ Fallback to DuckDuckGo

**Quality:** ⭐⭐⭐⭐ (8/10)
**Speed:** ⚡⚡⚡⚡ (Fast - parallel)
**Setup:** Medium (requires Google API key + CSE ID)

**Use When:**
- You have Google Custom Search API credentials
- Google ADK is not available
- You want good quality with LangChain processing

**Run:**
```bash
# Set environment variables
export GOOGLE_API_KEY='your-api-key'
export GOOGLE_CSE_ID='your-cse-id'
python langchain_google_pipeline.py
```

---

## ⚡ 3. Parallel Expansion Pipeline

**File:** `parallel_expansion_pipeline.py`

**Features:**
- ✅ 10 parallel workers (10x faster)
- ✅ Wikipedia API
- ✅ arXiv API
- ✅ DuckDuckGo search
- ✅ ChromaDB storage
- ✅ Thread-safe operations

**Quality:** ⭐⭐⭐ (6/10)
**Speed:** ⚡⚡⚡⚡⚡ (Very fast - 10 workers)
**Setup:** Simple (no API keys needed)

**Use When:**
- You don't have API keys
- You want maximum speed
- You're okay with medium quality

**Run:**
```bash
python parallel_expansion_pipeline.py
```

---

## 🐢 4. Knowledge Expansion Pipeline (Sequential)

**File:** `knowledge_expansion_pipeline.py`

**Features:**
- ✅ Wikipedia API
- ✅ arXiv API
- ✅ DuckDuckGo search
- ✅ ChromaDB storage
- ✅ Sequential processing
- ✅ Polite crawling (2s delays)

**Quality:** ⭐⭐⭐ (6/10)
**Speed:** ⚡⚡ (Slow - sequential)
**Setup:** Simple (no API keys needed)

**Use When:**
- You have limited bandwidth
- You want to be very polite to servers
- Speed is not important

**Run:**
```bash
python knowledge_expansion_pipeline.py
```

---

## 📊 Quick Comparison

| Pipeline | Quality | Speed | Setup | Recommended |
|----------|---------|-------|-------|-------------|
| **Ultimate ADK LangChain** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Medium | **YES** ⭐ |
| LangChain Google | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Medium | If no ADK |
| Parallel Expansion | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ | Simple | Fast & simple |
| Sequential Expansion | ⭐⭐⭐ | ⚡⚡ | Simple | Polite crawling |

---

## 🎯 Which One Should I Use?

### For BEST Results:
👉 **Use `ultimate_adk_langchain_pipeline.py`**
- Highest quality sources
- Google ADK's official google_search tool
- LangChain's robust processing
- Perfect for building the largest KB

### For Speed Without Setup:
👉 **Use `parallel_expansion_pipeline.py`**
- No API keys needed
- 10x faster than sequential
- Good enough for testing

### For Respectful Crawling:
👉 **Use `knowledge_expansion_pipeline.py`**
- Polite delays
- Sequential processing
- Safest option

---

## 🔧 Configuration

### All Pipelines Support:

**Max Topics:**
```python
MAX_TOPICS = 50   # Process 50 topics
MAX_TOPICS = None  # Process ALL topics (4,194+)
```

**Workers (Parallel Pipelines):**
```python
MAX_WORKERS = 5   # Recommended
MAX_WORKERS = 10  # Maximum speed
```

---

## 📈 Expected Results

### 50 Topics:
- **Time:** 1-3 hours (parallel) / 5-8 hours (sequential)
- **Chunks:** 750-1,000
- **Quality:** Depends on pipeline

### 100 Topics:
- **Time:** 2-5 hours (parallel) / 10-15 hours (sequential)
- **Chunks:** 1,500-2,000
- **Quality:** Depends on pipeline

### ALL 4,194 Topics:
- **Time:** 2-4 days (parallel) / 1-2 weeks (sequential)
- **Chunks:** 60,000-80,000
- **Quality:** Depends on pipeline
- **Storage:** 6-8 GB ChromaDB

---

## 📚 Documentation

- `ULTIMATE_ADK_PIPELINE_GUIDE.md` - Complete guide for Ultimate pipeline
- `KNOWLEDGE_EXPANSION_GUIDE.md` - General expansion guide
- `VECTOR_RAG_SUMMARY.md` - Vector RAG explanation

---

## 🚀 Quick Start

### 1. Install Dependencies:

```bash
# For Ultimate ADK LangChain (RECOMMENDED):
pip install google-genai chromadb langchain langchain-community beautifulsoup4 lxml

# For LangChain Google:
pip install chromadb langchain langchain-community beautifulsoup4 lxml

# For Parallel/Sequential:
pip install chromadb requests beautifulsoup4 lxml
```

### 2. Run Your Chosen Pipeline:

```bash
# BEST (recommended):
python ultimate_adk_langchain_pipeline.py

# Or alternative:
python parallel_expansion_pipeline.py
```

### 3. Monitor Progress:

Watch the console for:
```
📊 Progress: 10/50 topics | Total chunks: 287
```

### 4. Check Results:

```python
from ultimate_adk_langchain_pipeline import UltimateADKLangChainPipeline

pipeline = UltimateADKLangChainPipeline(gemini_api_key="YOUR_KEY")
stats = pipeline.get_stats()

print(f"Total chunks: {stats['total_chunks']:,}")
print(f"Topics processed: {stats['topics_processed']}")
```

---

## 🎊 Final Recommendation

### For Production Use:
✅ **Use `ultimate_adk_langchain_pipeline.py`**

**Why:**
1. Highest quality search results (Google ADK)
2. Most robust scraping (LangChain)
3. Best text chunking (LangChain)
4. Parallel processing (fast)
5. ChromaDB vector storage (semantic search)

**Result:** The LARGEST and HIGHEST QUALITY knowledge base!

---

## 📞 Support

See individual pipeline files for detailed documentation and troubleshooting.

**Questions?** Check the guide files:
- `ULTIMATE_ADK_PIPELINE_GUIDE.md` - For Ultimate pipeline
- `KNOWLEDGE_EXPANSION_GUIDE.md` - For general info
