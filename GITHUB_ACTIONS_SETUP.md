## 🚀 GitHub Actions + Pages Setup Guide

This guide shows you how to run the knowledge expansion pipeline on GitHub Actions and deploy to GitHub Pages automatically.

---

## 📋 Prerequisites

1. GitHub repository (you have this: `rinit2994-art/AI_INTERVIEW`)
2. Gemini API key (you have this: `AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU`)
3. GitHub Pages enabled

---

## 🔧 Setup Steps

### 1. Add Gemini API Key to GitHub Secrets

1. Go to your repository: https://github.com/rinit2994-art/AI_INTERVIEW
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: `AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU`
6. Click **Add secret**

### 2. Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** → **/ (root)**
4. Click **Save**

### 3. Enable GitHub Actions

1. Go to **Actions** tab
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see the workflow: **Expand Knowledge Base and Deploy**

---

## ▶️ Running the Pipeline

### Manual Trigger (Recommended for First Run)

1. Go to **Actions** tab
2. Click **Expand Knowledge Base and Deploy** workflow
3. Click **Run workflow** dropdown
4. Click **Run workflow** button
5. Wait 2-3 hours for completion

### What Happens

**The workflow will:**

1. ✅ Checkout your repository
2. ✅ Install Python 3.11 + dependencies
3. ✅ Run parallel expansion pipeline with 100 topics
4. ✅ Scrape internet for relevant content (Wikipedia, arXiv, Web)
5. ✅ Create ChromaDB with all documents
6. ✅ Export to JSON for GitHub Pages
7. ✅ Generate search index
8. ✅ Commit changes to repository
9. ✅ Deploy to GitHub Pages

**Result:**
- 📊 ~1,500-2,000 documents from 100 topics
- 🌐 Live at: https://rinit2994-art.github.io/AI_INTERVIEW/
- 🔍 Client-side search (no server needed!)

### Automatic Weekly Runs

The workflow runs automatically every **Sunday at midnight** to keep your knowledge base fresh with new content.

---

## 📊 Expected Results

### After First Run (100 topics):
```
Total Documents:     ~1,500-2,000
Topics Processed:    100
Unique URLs Scraped: ~400-500
Storage:            ~150-200 MB
Processing Time:    2-3 hours
```

### After Multiple Runs:
```
Total Documents:     ~10,000+
Topics Processed:    500+
Unique URLs Scraped: ~2,000+
Storage:            ~1-2 GB
```

### Full Expansion (modify workflow to process ALL topics):
```
Total Documents:     ~60,000-80,000
Topics Processed:    4,194
Unique URLs Scraped: ~15,000-20,000
Storage:            ~6-8 GB
Processing Time:    6+ hours
```

---

## 🎯 Customize Pipeline

### Process More Topics

Edit `.github/workflows/expand-knowledge-base.yml`:

```yaml
# Line ~36: Change max_topics
pipeline.run_parallel_pipeline(max_topics=100)  # Change 100 to 500, 1000, or None
```

**Options:**
- `max_topics=100` - Quick run (2-3 hours, ~1,500 docs)
- `max_topics=500` - Medium run (6-8 hours, ~7,500 docs)
- `max_topics=None` - Full run (6-12 hours, ~60,000 docs)

### Adjust Workers

```python
pipeline = ParallelKnowledgeExpansion(max_workers=5)  # Change 5 to 3-10
```

**Recommendations:**
- `max_workers=3` - Safer, slower
- `max_workers=5` - Balanced (default)
- `max_workers=10` - Faster, may hit rate limits

### Change Schedule

```yaml
schedule:
  - cron: '0 0 * * 0'  # Every Sunday at midnight
```

**Options:**
- Daily: `'0 0 * * *'`
- Twice weekly: `'0 0 * * 0,3'` (Sunday & Wednesday)
- Monthly: `'0 0 1 * *'` (1st of each month)

---

## 📁 Files Created

After running the workflow:

### In Your Repository:
- `docs/expanded_knowledge.json` - All documents (large file)
- `docs/search_index.json` - Searchable index
- `docs/index_enhanced.html` - Enhanced search UI

### On GitHub Pages:
- https://rinit2994-art.github.io/AI_INTERVIEW/
- https://rinit2994-art.github.io/AI_INTERVIEW/index_enhanced.html

---

## 🔍 Using the Enhanced Search

### Access the Site:
1. Go to: https://rinit2994-art.github.io/AI_INTERVIEW/index_enhanced.html
2. Enter your question in the search box
3. Click **Search** or press Enter
4. View results with similarity scores

### Features:
- ✅ Client-side search (fast, no server needed)
- ✅ Similarity scoring (0-100% match)
- ✅ Category filtering
- ✅ Keyword highlighting
- ✅ Topic-based grouping
- ✅ Source attribution

### Example Queries:
```
"What is MCP server?"
"How do transformers work?"
"Explain ChromaDB"
"A2A protocol details"
"Latest RAG techniques"
```

---

## 🚧 Troubleshooting

### Workflow Fails

**Issue:** "Resource not accessible by integration"
**Fix:** Enable read/write permissions:
1. Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Save

**Issue:** "Timeout"
**Fix:** The workflow has a 6-hour limit. If it times out:
1. Reduce `max_topics` in workflow
2. Run multiple times (it skips processed topics)

**Issue:** "Quota exceeded"
**Fix:** Gemini API quota hit:
1. Wait 24 hours
2. Reduce `max_workers` to 3
3. Add delays in pipeline

### Search Not Working

**Issue:** "Knowledge base is still loading"
**Fix:**
1. Check if `search_index.json` exists in `docs/`
2. Run workflow to generate it
3. Clear browser cache

**Issue:** "No results found"
**Fix:**
1. Check if workflow completed successfully
2. Verify `search_index.json` has content
3. Try different search terms

---

## 💡 Advanced Configuration

### Use Different Pipeline

Edit workflow to use **Ultimate ADK + LangChain pipeline**:

```python
# Replace parallel_expansion_pipeline with:
from ultimate_adk_langchain_pipeline import UltimateADKLangChainPipeline

pipeline = UltimateADKLangChainPipeline(
    gemini_api_key="${{ secrets.GEMINI_API_KEY }}",
    max_workers=5
)
pipeline.run_pipeline(max_topics=100, parallel=True)
```

**Benefits:**
- Google ADK google_search (highest quality)
- LangChain processing (robust)
- Better content quality

### Add More Sources

Edit `parallel_expansion_pipeline.py` to add:
- GitHub repositories
- Stack Overflow
- Medium articles
- YouTube transcripts

---

## 📊 Monitoring

### View Workflow Status:
1. Go to **Actions** tab
2. Click on latest run
3. View logs for each step
4. Check "Run knowledge expansion pipeline" for progress

### Check Knowledge Base Size:
1. Visit: https://rinit2994-art.github.io/AI_INTERVIEW/index_enhanced.html
2. View stats at top:
   - Total Documents
   - Categories
   - Original Entries

### Monitor Storage:
1. Go to repository **Insights** → **Traffic**
2. Check repository size (should be < 1 GB initially)
3. Large files go to `docs/expanded_knowledge.json`

---

## 🎊 Success Metrics

After setup is complete:

✅ **GitHub Actions workflow runs successfully**
✅ **Knowledge base expands weekly automatically**
✅ **GitHub Pages site is live and searchable**
✅ **Search returns relevant results**
✅ **Stats show increasing document count**

---

## 🚀 Next Steps

1. **Run workflow now** (manually trigger first run)
2. **Wait 2-3 hours** for completion
3. **Visit GitHub Pages** to test search
4. **Let it run weekly** for continuous expansion
5. **After a month**: 10,000+ documents!
6. **After 6 months**: 50,000+ documents!

---

## 📞 Support

**Issues?**
- Check GitHub Actions logs
- Verify API key is set correctly
- Ensure GitHub Pages is enabled
- Review workflow file syntax

**Questions?**
- See: `ULTIMATE_ADK_PIPELINE_GUIDE.md`
- See: `PIPELINES_README.md`
- See: `FINAL_DELIVERY_SUMMARY.md`

---

**Your knowledge base will grow AUTOMATICALLY every week! 🚀**
