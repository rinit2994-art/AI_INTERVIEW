"""
AGENTIC RAG SYSTEM - Multi-Agent Orchestration (Simplified)
Uses Gemini AI for intelligent agent coordination
Decides: Sequential vs Parallel vs Routing based on query complexity
Works in restricted environments
"""

import logging
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from knowledge_base_manager_v2 import KnowledgeBaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Agentic RAG System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded API Key
GEMINI_API_KEY = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"
genai.configure(api_key=GEMINI_API_KEY)


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class AgenticRAG:
    """Multi-Agent RAG with Orchestration."""

    def __init__(self):
        logger.info("🚀 Initializing Agentic RAG System...")

        # Load knowledge base
        self.kb = KnowledgeBaseManager()
        self.kb.parse_typescript_kb()
        self.kb.build_indexes()

        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        logger.info(f"✅ Loaded {len(self.kb.entries):,} entries")

    def decide_strategy(self, question: str) -> str:
        """Coordinator Agent - decides processing strategy."""
        try:
            prompt = f"""Analyze this query and decide the best strategy:

Query: "{question}"

Strategies:
- SIMPLE: Single concept (e.g., "what is X?")
- COMPARE: Comparing topics (e.g., "X vs Y")
- USE_CASES: Asking for examples/use cases
- DEEP: Needs detailed explanation

Return ONLY: SIMPLE, COMPARE, USE_CASES, or DEEP"""

            response = self.model.generate_content(prompt)
            strategy = response.text.strip().upper()

            valid = ["SIMPLE", "COMPARE", "USE_CASES", "DEEP"]
            return strategy if strategy in valid else "SIMPLE"

        except:
            return "SIMPLE"

    def extract_topics(self, question: str) -> List[str]:
        """Search Agent - extracts key topics to search."""
        try:
            prompt = f"""Extract 2-3 KEY TOPICS to search for:

Query: "{question}"

Return only the topics, one per line."""

            response = self.model.generate_content(prompt)
            topics = [t.strip() for t in response.text.strip().split('\n') if t.strip()]
            return topics[:3]

        except:
            return [w for w in question.split() if len(w) > 3][:3]

    def search_kb(self, topics: List[str], top_k: int = 5) -> List[Dict]:
        """Search knowledge base for topics."""
        all_results = []
        seen = set()

        for topic in topics:
            results = self.kb.search(topic, top_k=top_k)
            for r in results:
                if r['title'] not in seen:
                    seen.add(r['title'])
                    all_results.append(r)

        return sorted(all_results, key=lambda x: x.get('score', 0), reverse=True)[:top_k * 2]

    def process_simple(self, question: str, docs: List[Dict]) -> str:
        """Generate simple, comprehensive answer."""
        if not docs:
            return "No relevant information found in knowledge base."

        context = "\n\n".join([
            f"**{doc['title']}**\n{doc['content']}"
            for doc in docs[:2]
        ])

        prompt = f"""Answer this question comprehensively using the context below.

Question: {question}

Context:
{context}

Requirements:
- Give a COMPLETE answer
- Include all important details
- Use bullet points for clarity
- NO TRUNCATION - full explanations
- Add examples if applicable"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return context

    def process_compare(self, question: str, docs: List[Dict]) -> str:
        """Generate comparative answer."""
        if not docs:
            return "No relevant information found."

        context = "\n\n".join([
            f"**{doc['title']}**\n{doc['content']}"
            for doc in docs[:4]
        ])

        prompt = f"""Compare and contrast based on this question.

Question: {question}

Available information:
{context}

Requirements:
- Show similarities and differences
- Use clear structure
- Include specific examples
- Be thorough and complete
- NO TRUNCATION"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return context

    def process_use_cases(self, question: str, docs: List[Dict]) -> str:
        """Generate use case examples."""
        if not docs:
            return "No relevant information found."

        context = "\n\n".join([
            f"**{doc['title']}**\n{doc['content']}"
            for doc in docs[:3]
        ])

        prompt = f"""Provide comprehensive use cases and examples.

Question: {question}

Context:
{context}

Requirements:
- List real-world use cases
- Give specific examples
- Include step-by-step scenarios
- Show practical applications
- Be detailed and complete"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return context

    def process_deep(self, question: str, docs: List[Dict]) -> str:
        """Generate deep, comprehensive explanation."""
        if not docs:
            return "No relevant information found."

        # First, analyze each document
        analyses = []
        for doc in docs[:3]:
            try:
                analysis_prompt = f"""Analyze this content for: {question}

Content: {doc['content'][:1000]}

Extract key points relevant to the question."""

                response = self.model.generate_content(analysis_prompt)
                analyses.append(f"**{doc['title']}**:\n{response.text}")
            except:
                analyses.append(f"**{doc['title']}**:\n{doc['content'][:500]}")

        # Then synthesize
        synthesis_prompt = f"""Create a deep, comprehensive answer.

Question: {question}

Analysis from multiple sources:
{chr(10).join(analyses)}

Requirements:
- Synthesize all information
- Explain thoroughly
- Include technical details
- Show relationships
- Give examples
- Be complete - NO TRUNCATION"""

        try:
            response = self.model.generate_content(synthesis_prompt)
            return response.text
        except:
            return '\n\n'.join(analyses)

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Main orchestration - routes to best strategy."""
        logger.info(f"🔍 Query: {question}")

        # Step 1: Decide strategy
        strategy = self.decide_strategy(question)
        logger.info(f"📊 Strategy: {strategy}")

        # Step 2: Extract topics
        topics = self.extract_topics(question)
        logger.info(f"🔎 Topics: {topics}")

        # Step 3: Search knowledge base
        docs = self.search_kb(topics, top_k=top_k)
        logger.info(f"📚 Found {len(docs)} documents")

        # Step 4: Generate answer based on strategy
        if strategy == "SIMPLE":
            answer = self.process_simple(question, docs)
        elif strategy == "COMPARE":
            answer = self.process_compare(question, docs)
        elif strategy == "USE_CASES":
            answer = self.process_use_cases(question, docs)
        elif strategy == "DEEP":
            answer = self.process_deep(question, docs)
        else:
            answer = self.process_simple(question, docs)

        return {
            "answer": answer,
            "sources": docs,
            "strategy": strategy,
            "topics_searched": topics,
            "docs_found": len(docs)
        }


# Initialize
rag = AgenticRAG()


@app.get("/")
async def home():
    return FileResponse("../docs/index.html")


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "system": "Multi-Agent Agentic RAG",
        "total_documents": len(rag.kb.entries),
        "strategies": ["SIMPLE", "COMPARE", "USE_CASES", "DEEP"]
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        result = rag.query(request.question, request.top_k)

        return {
            "answer": result["answer"],
            "sources": [
                {
                    "title": s['title'],
                    "content": s['content'],  # FULL content, no truncation!
                    "category": s.get('category', 'General'),
                    "score": s.get('score', 0)
                }
                for s in result["sources"][:5]
            ],
            "metadata": {
                "strategy": result["strategy"],
                "topics_searched": result["topics_searched"],
                "documents_found": result["docs_found"]
            }
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "metadata": {"error": str(e)}
        }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🤖 AGENTIC RAG - Multi-Agent Orchestration")
    print("="*80)
    print("\n✨ Agents:")
    print("  • Coordinator - Decides best strategy")
    print("  • Search - Extracts optimal topics")
    print("  • Answer - Generates comprehensive responses")
    print("\n📊 Strategies:")
    print("  • SIMPLE - Direct answers")
    print("  • COMPARE - Comparisons")
    print("  • USE_CASES - Examples & use cases")
    print("  • DEEP - Comprehensive analysis")
    print(f"\n📚 Knowledge Base: {len(rag.kb.entries):,} entries")
    print("="*80 + "\n")

    print("🌐 Server: http://localhost:8000\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
