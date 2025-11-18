"""
AGENTIC RAG SYSTEM - Multi-Agent Orchestration
Uses Google ADK for intelligent agent coordination
Decides: Sequential vs Parallel vs Routing based on query complexity
"""

import logging
from typing import List, Dict, Any, Optional
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
client = genai.Client(api_key=GEMINI_API_KEY)


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class AgenticRAGSystem:
    """
    Multi-Agent RAG System with Orchestration.

    Agents:
    1. Coordinator Agent - Decides strategy (sequential/parallel/routing)
    2. Search Agent - Finds relevant documents
    3. Analysis Agent - Analyzes and extracts key info
    4. Answer Agent - Generates comprehensive answers
    """

    def __init__(self):
        logger.info("🚀 Initializing Agentic RAG System...")

        # Load knowledge base
        self.kb_manager = KnowledgeBaseManager()
        self.kb_manager.parse_typescript_kb()
        self.kb_manager.build_indexes()

        logger.info(f"✅ Loaded {len(self.kb_manager.entries)} knowledge entries")

        # Initialize agents
        self._init_agents()

    def _init_agents(self):
        """Initialize all agents with specific roles."""

        # 1. Coordinator Agent - Decides how to process query
        self.coordinator_agent = types.Agent(
            model="gemini-2.0-flash-exp",
            name="coordinator",
            instruction="""You are the Coordinator Agent. Your job is to analyze the user's query
            and decide the best strategy to answer it.

            Strategies:
            - SIMPLE: Single topic, direct answer (e.g., "what is X?")
            - MULTI_TOPIC: Multiple related topics need to be combined (e.g., "compare X and Y")
            - COMPLEX: Needs deep analysis with multiple steps (e.g., "how do X and Y work together?")
            - USE_CASES: User asking for examples or use cases

            Return ONLY the strategy name: SIMPLE, MULTI_TOPIC, COMPLEX, or USE_CASES"""
        )

        # 2. Search Agent - Finds relevant documents
        self.search_agent = types.Agent(
            model="gemini-2.0-flash-exp",
            name="searcher",
            instruction="""You are the Search Agent. Given a query, extract the KEY TOPICS to search for.

            Return a JSON array of search terms, e.g., ["MCP", "server", "implementation"]

            Focus on:
            - Main concepts
            - Technical terms
            - Specific keywords

            Return ONLY the JSON array, nothing else."""
        )

        # 3. Analysis Agent - Analyzes documents
        self.analysis_agent = types.Agent(
            model="gemini-2.0-flash-exp",
            name="analyzer",
            instruction="""You are the Analysis Agent. Given documents about a topic, extract:

            1. Key concepts
            2. Important details
            3. Relationships
            4. Examples

            Synthesize the information clearly and concisely."""
        )

        # 4. Answer Agent - Generates final answer
        self.answer_agent = types.Agent(
            model="gemini-2.0-flash-exp",
            name="answerer",
            instruction="""You are the Answer Agent. Generate a COMPLETE, COMPREHENSIVE answer.

            Requirements:
            - Be thorough and detailed
            - Include all relevant information
            - Use bullet points and structure
            - Give examples when applicable
            - NO TRUNCATION - full answers only

            Format with:
            • Clear sections
            • Bullet points
            • Examples
            • Complete explanations"""
        )

        logger.info("✅ All agents initialized")

    def decide_strategy(self, question: str) -> str:
        """Use coordinator agent to decide processing strategy."""
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"Query: {question}\n\nDecide strategy:",
                config=types.GenerateContentConfig(
                    system_instruction=self.coordinator_agent.instruction,
                    temperature=0.1
                )
            )

            strategy = response.text.strip().upper()

            # Validate strategy
            valid_strategies = ["SIMPLE", "MULTI_TOPIC", "COMPLEX", "USE_CASES"]
            if strategy not in valid_strategies:
                strategy = "SIMPLE"

            logger.info(f"📊 Strategy decided: {strategy}")
            return strategy

        except Exception as e:
            logger.error(f"Strategy decision error: {e}")
            return "SIMPLE"

    def extract_search_terms(self, question: str) -> List[str]:
        """Use search agent to extract key search terms."""
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"Query: {question}\n\nExtract search terms:",
                config=types.GenerateContentConfig(
                    system_instruction=self.search_agent.instruction,
                    temperature=0.1
                )
            )

            # Parse JSON response
            import json
            terms = json.loads(response.text.strip())
            logger.info(f"🔍 Search terms: {terms}")
            return terms

        except Exception as e:
            logger.error(f"Search term extraction error: {e}")
            # Fallback: use question words
            return [w for w in question.split() if len(w) > 3][:5]

    def search_knowledge_base(self, search_terms: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant documents."""
        all_results = []
        seen_titles = set()

        for term in search_terms:
            results = self.kb_manager.search(term, top_k=top_k)

            for result in results:
                title = result['title']
                if title not in seen_titles:
                    seen_titles.add(title)
                    all_results.append(result)

        # Sort by score and limit
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_results[:top_k * 2]  # Return more documents for better coverage

    def process_simple(self, question: str, top_k: int) -> Dict[str, Any]:
        """Process simple query - single topic."""
        logger.info("📝 Processing as SIMPLE query")

        # Extract search terms
        search_terms = self.extract_search_terms(question)

        # Search knowledge base
        documents = self.search_knowledge_base(search_terms, top_k=top_k)

        if not documents:
            return {
                "answer": "I couldn't find relevant information in the knowledge base.",
                "sources": [],
                "strategy": "SIMPLE",
                "documents_used": 0
            }

        # Generate answer using answer agent
        context = "\n\n".join([
            f"Document: {doc['title']}\n{doc['content']}"
            for doc in documents[:3]  # Use top 3 documents
        ])

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"""Question: {question}

Context from knowledge base:
{context}

Generate a comprehensive answer based on the context above.""",
                config=types.GenerateContentConfig(
                    system_instruction=self.answer_agent.instruction,
                    temperature=0.3
                )
            )

            answer = response.text

        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            # Fallback: return document content directly
            answer = documents[0]['content']

        return {
            "answer": answer,
            "sources": documents,
            "strategy": "SIMPLE",
            "documents_used": len(documents)
        }

    def process_multi_topic(self, question: str, top_k: int) -> Dict[str, Any]:
        """Process multi-topic query - needs combining multiple topics."""
        logger.info("📝 Processing as MULTI_TOPIC query")

        # Extract search terms (multiple topics)
        search_terms = self.extract_search_terms(question)

        # Search for each topic separately
        all_documents = []
        for term in search_terms:
            docs = self.kb_manager.search(term, top_k=3)
            all_documents.extend(docs)

        if not all_documents:
            return {
                "answer": "I couldn't find relevant information in the knowledge base.",
                "sources": [],
                "strategy": "MULTI_TOPIC",
                "documents_used": 0
            }

        # Remove duplicates by title
        seen_titles = set()
        unique_docs = []
        for doc in all_documents:
            if doc['title'] not in seen_titles:
                seen_titles.add(doc['title'])
                unique_docs.append(doc)

        # Combine information from all documents
        context = "\n\n".join([
            f"Topic: {doc['title']}\n{doc['content']}"
            for doc in unique_docs[:5]  # Use top 5 unique documents
        ])

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"""Question: {question}

Multiple relevant topics found:
{context}

Synthesize a comprehensive answer that combines information from all topics above.
Show how they relate to each other.""",
                config=types.GenerateContentConfig(
                    system_instruction=self.answer_agent.instruction,
                    temperature=0.3
                )
            )

            answer = response.text

        except Exception as e:
            logger.error(f"Multi-topic answer error: {e}")
            answer = "\n\n".join([doc['content'][:500] for doc in unique_docs[:3]])

        return {
            "answer": answer,
            "sources": unique_docs,
            "strategy": "MULTI_TOPIC",
            "documents_used": len(unique_docs)
        }

    def process_complex(self, question: str, top_k: int) -> Dict[str, Any]:
        """Process complex query - needs deep analysis."""
        logger.info("📝 Processing as COMPLEX query")

        # Step 1: Extract search terms
        search_terms = self.extract_search_terms(question)

        # Step 2: Search knowledge base
        documents = self.search_knowledge_base(search_terms, top_k=top_k)

        if not documents:
            return self.process_simple(question, top_k)  # Fallback

        # Step 3: Analyze each document
        analyses = []
        for doc in documents[:5]:
            try:
                analysis_response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=f"""Analyze this document:

Title: {doc['title']}
Content: {doc['content']}

Extract key points relevant to: {question}""",
                    config=types.GenerateContentConfig(
                        system_instruction=self.analysis_agent.instruction,
                        temperature=0.2
                    )
                )

                analyses.append({
                    'title': doc['title'],
                    'analysis': analysis_response.text
                })

            except Exception as e:
                logger.error(f"Analysis error: {e}")
                continue

        # Step 4: Generate comprehensive answer
        analysis_context = "\n\n".join([
            f"{a['title']}:\n{a['analysis']}"
            for a in analyses
        ])

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"""Question: {question}

Detailed analysis of relevant topics:
{analysis_context}

Generate a deep, comprehensive answer that:
1. Addresses all aspects of the question
2. Combines insights from multiple sources
3. Provides detailed explanations
4. Includes examples
5. Shows relationships and connections""",
                config=types.GenerateContentConfig(
                    system_instruction=self.answer_agent.instruction,
                    temperature=0.3
                )
            )

            answer = response.text

        except Exception as e:
            logger.error(f"Complex answer error: {e}")
            answer = analysis_context

        return {
            "answer": answer,
            "sources": documents,
            "strategy": "COMPLEX",
            "documents_used": len(documents),
            "analyses_performed": len(analyses)
        }

    def process_use_cases(self, question: str, top_k: int) -> Dict[str, Any]:
        """Process use case query - extract and generate examples."""
        logger.info("📝 Processing as USE_CASES query")

        # Extract main topic
        search_terms = self.extract_search_terms(question)

        # Search knowledge base
        documents = self.search_knowledge_base(search_terms, top_k=top_k)

        if not documents:
            return self.process_simple(question, top_k)

        # Generate use cases
        context = "\n\n".join([
            f"{doc['title']}\n{doc['content']}"
            for doc in documents[:3]
        ])

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"""Question: {question}

Context:
{context}

Generate comprehensive use cases and examples. Include:
1. Real-world applications
2. Specific examples
3. Step-by-step scenarios
4. Best practices
5. Common patterns""",
                config=types.GenerateContentConfig(
                    system_instruction=self.answer_agent.instruction,
                    temperature=0.4
                )
            )

            answer = response.text

        except Exception as e:
            logger.error(f"Use cases error: {e}")
            answer = context

        return {
            "answer": answer,
            "sources": documents,
            "strategy": "USE_CASES",
            "documents_used": len(documents)
        }

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Main query method - orchestrates agents."""
        logger.info(f"🔍 Query: {question}")

        # Step 1: Decide strategy
        strategy = self.decide_strategy(question)

        # Step 2: Process based on strategy
        if strategy == "SIMPLE":
            return self.process_simple(question, top_k)
        elif strategy == "MULTI_TOPIC":
            return self.process_multi_topic(question, top_k)
        elif strategy == "COMPLEX":
            return self.process_complex(question, top_k)
        elif strategy == "USE_CASES":
            return self.process_use_cases(question, top_k)
        else:
            return self.process_simple(question, top_k)


# Initialize system
rag_system = AgenticRAGSystem()


@app.get("/")
async def home():
    """Serve the frontend."""
    return FileResponse("../docs/index.html")


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "system": "Agentic RAG with Multi-Agent Orchestration",
        "agents": ["Coordinator", "Search", "Analysis", "Answer"],
        "total_documents": len(rag_system.kb_manager.entries)
    }


@app.get("/api/stats")
async def stats():
    """Get system statistics."""
    return {
        "total_entries": len(rag_system.kb_manager.entries),
        "categories": 8,
        "unique_keywords": 5833,
        "system_type": "Multi-Agent Agentic RAG",
        "strategies": ["SIMPLE", "MULTI_TOPIC", "COMPLEX", "USE_CASES"]
    }


@app.post("/api/query")
async def query(request: QueryRequest):
    """Query with agentic orchestration."""
    try:
        result = rag_system.query(request.question, request.top_k)

        return {
            "answer": result["answer"],
            "sources": [
                {
                    "title": s['title'],
                    "content": s['content'][:500] + "..." if len(s['content']) > 500 else s['content'],
                    "category": s.get('category', 'General'),
                    "score": s.get('score', 0)
                }
                for s in result["sources"]
            ],
            "metadata": {
                "strategy": result["strategy"],
                "documents_used": result["documents_used"],
                "total_available": len(rag_system.kb_manager.entries)
            }
        }

    except Exception as e:
        logger.error(f"Query error: {e}")
        return {
            "answer": f"Error processing query: {str(e)}",
            "sources": [],
            "metadata": {"error": str(e)}
        }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🤖 AGENTIC RAG SYSTEM - Multi-Agent Orchestration")
    print("="*80)
    print("\n✨ Features:")
    print("  • Coordinator Agent - Decides best strategy")
    print("  • Search Agent - Extracts optimal search terms")
    print("  • Analysis Agent - Deep document analysis")
    print("  • Answer Agent - Comprehensive answer generation")
    print("\n📊 Strategies:")
    print("  • SIMPLE - Single topic queries")
    print("  • MULTI_TOPIC - Compare/combine multiple topics")
    print("  • COMPLEX - Deep analysis with multiple steps")
    print("  • USE_CASES - Example-focused responses")
    print("\n" + "="*80)
    print(f"📚 Knowledge Base: {len(rag_system.kb_manager.entries):,} entries")
    print("="*80 + "\n")

    print("🌐 Starting server at http://localhost:8000")
    print("\n" + "="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
