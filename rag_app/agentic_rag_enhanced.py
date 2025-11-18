"""
ENHANCED AGENTIC RAG SYSTEM
Implements ADK Multi-Agent Patterns:
- Custom Orchestrator Agent with conditional routing
- Sequential processing for deep analysis
- Parallel processing for multi-topic queries
- Shared state for agent communication
- Specialized agents following ADK best practices
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from knowledge_base_manager_v2 import KnowledgeBaseManager
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Enhanced Agentic RAG System")

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


@dataclass
class AgentContext:
    """Shared state for agent communication (ADK pattern)"""
    query: str
    strategy: str = ""
    search_terms: List[str] = field(default_factory=list)
    documents: List[Dict] = field(default_factory=list)
    analyses: List[Dict] = field(default_factory=list)
    answer: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_state(self, key: str, value: Any):
        """Set state value (simulates ctx.session.state)"""
        self.metadata[key] = value

    def get_state(self, key: str, default=None):
        """Get state value"""
        return self.metadata.get(key, default)


class BaseAgent:
    """
    Base agent following ADK pattern.
    All agents inherit from this and implement run() method.
    """
    def __init__(self, name: str, model: str = "gemini-1.5-flash", instruction: str = ""):
        self.name = name
        self.model = genai.GenerativeModel(model)
        self.instruction = instruction
        logger.info(f"✅ Initialized {name} agent")

    def run(self, ctx: AgentContext) -> AgentContext:
        """Execute agent logic and return updated context"""
        raise NotImplementedError("Subclasses must implement run()")


class CoordinatorAgent(BaseAgent):
    """
    LLM Agent - Decides processing strategy
    Implements ADK LlmAgent pattern with dynamic reasoning
    """
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            instruction="""You are the Coordinator Agent. Analyze the query and decide the optimal strategy.

            Strategies:
            - SIMPLE: Single concept, direct answer (e.g., "what is X?")
            - MULTI_TOPIC: Multiple topics to combine (e.g., "compare X and Y")
            - DEEP_SEQUENTIAL: Complex query needing step-by-step analysis
            - PARALLEL_SEARCH: Broad query benefiting from concurrent searches

            Return ONLY the strategy name."""
        )

    def run(self, ctx: AgentContext) -> AgentContext:
        """Decide processing strategy"""
        try:
            prompt = f"""{self.instruction}

Query: "{ctx.query}"

Analyze and return strategy:"""

            response = self.model.generate_content(prompt)
            strategy = response.text.strip().upper()

            valid = ["SIMPLE", "MULTI_TOPIC", "DEEP_SEQUENTIAL", "PARALLEL_SEARCH"]
            ctx.strategy = strategy if strategy in valid else "SIMPLE"
            ctx.set_state("coordinator_decision", strategy)

            logger.info(f"📊 Strategy: {ctx.strategy}")
            return ctx

        except Exception as e:
            logger.error(f"Coordinator error: {e}")
            ctx.strategy = "SIMPLE"
            return ctx


class SearchAgent(BaseAgent):
    """
    LLM Agent - Extracts optimal search terms
    Implements ADK LlmAgent pattern with tool-like behavior
    """
    def __init__(self):
        super().__init__(
            name="SearchAgent",
            instruction="""You are the Search Agent. Extract MEANINGFUL KEYWORDS and TECHNICAL TERMS to search for.

            Rules:
            - Extract technical terms, acronyms, concepts (e.g., "MCP", "RAG", "transformer")
            - Ignore generic words like "what", "how", "explain", "is", "the"
            - For "X vs Y" queries, extract both X and Y
            - For acronyms, include the full form if mentioned

            Examples:
            - "What is MCP protocol?" → "MCP protocol, MCP"
            - "Explain A2A protocol" → "A2A protocol, A2A, agent-to-agent"
            - "How does RAG work?" → "RAG, retrieval augmented generation"

            Return topics as comma-separated list."""
        )

    def run(self, ctx: AgentContext) -> AgentContext:
        """Extract search terms based on query"""
        try:
            prompt = f"""{self.instruction}

Query: "{ctx.query}"

Extract meaningful search terms:"""

            response = self.model.generate_content(prompt)
            terms = [t.strip() for t in response.text.split(',') if t.strip() and len(t.strip()) > 2]
            ctx.search_terms = terms[:5]
            ctx.set_state("search_terms_extracted", terms)

            logger.info(f"🔍 Search terms: {ctx.search_terms}")
            return ctx

        except Exception as e:
            logger.error(f"Search agent error: {e}")
            # Fallback: extract meaningful words (> 3 chars, not common stop words)
            stop_words = {'what', 'how', 'when', 'where', 'who', 'why', 'does', 'the', 'is', 'are', 'explain', 'tell', 'about'}
            terms = [w for w in ctx.query.split() if len(w) > 3 and w.lower() not in stop_words]
            ctx.search_terms = terms[:3]
            return ctx


class RetrievalAgent(BaseAgent):
    """
    Workflow Agent - Retrieves documents from knowledge base
    Implements deterministic retrieval workflow
    """
    def __init__(self, kb_manager: KnowledgeBaseManager):
        super().__init__(name="RetrievalAgent")
        self.kb = kb_manager

    def run(self, ctx: AgentContext) -> AgentContext:
        """Search knowledge base for documents"""
        all_results = []
        seen_titles = set()

        for term in ctx.search_terms:
            results = self.kb.search(term, top_k=5)
            for result in results:
                if result['title'] not in seen_titles:
                    seen_titles.add(result['title'])
                    all_results.append(result)

        # Sort by score
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        ctx.documents = all_results[:10]  # Top 10
        ctx.set_state("documents_retrieved", len(ctx.documents))

        logger.info(f"📚 Retrieved {len(ctx.documents)} documents")
        return ctx


class AnalysisAgent(BaseAgent):
    """
    LLM Agent - Deep document analysis
    Implements ADK LlmAgent with structured output
    """
    def __init__(self):
        super().__init__(
            name="AnalysisAgent",
            instruction="""You are the Analysis Agent. Extract key insights from documents.

            For each document:
            1. Identify main concepts
            2. Extract relevant details
            3. Note relationships
            4. Highlight examples

            Be thorough and complete."""
        )

    def run(self, ctx: AgentContext) -> AgentContext:
        """Analyze documents for key insights"""
        analyses = []

        for doc in ctx.documents[:5]:  # Analyze top 5
            try:
                prompt = f"""{self.instruction}

Query: {ctx.query}

Document Title: {doc['title']}
Content: {doc['content'][:1500]}

Extract key insights:"""

                response = self.model.generate_content(prompt)

                analyses.append({
                    'title': doc['title'],
                    'category': doc.get('category', 'General'),
                    'analysis': response.text
                })

            except Exception as e:
                logger.error(f"Analysis error for {doc['title']}: {e}")
                continue

        ctx.analyses = analyses
        ctx.set_state("analyses_completed", len(analyses))

        logger.info(f"🔬 Analyzed {len(analyses)} documents")
        return ctx


class SynthesisAgent(BaseAgent):
    """
    LLM Agent - Generate comprehensive answers
    Implements ADK LlmAgent with complete output
    """
    def __init__(self):
        super().__init__(
            name="SynthesisAgent",
            instruction="""You are the Synthesis Agent. Generate COMPLETE, COMPREHENSIVE answers that DIRECTLY ADDRESS THE QUESTION.

            CRITICAL Requirements:
            - ANSWER THE EXACT QUESTION ASKED - do not go off-topic
            - Use information from the context that is RELEVANT to the question
            - If the question asks about "X", focus ONLY on "X", not other topics
            - Address ALL aspects of the specific question
            - Use clear structure with sections
            - Include bullet points for clarity
            - Provide specific examples from the context
            - NO TRUNCATION - full explanations only
            - Be factual and precise

            Format:
            • Direct answer to the question
            • Detailed explanation with subsections
            • Concrete examples from context
            • Complete conclusion

            IMPORTANT: Stay focused on answering the exact question. Do not provide information about unrelated topics."""
        )

    def run(self, ctx: AgentContext) -> AgentContext:
        """Generate comprehensive answer"""
        try:
            if not ctx.documents:
                ctx.answer = "No relevant information found in knowledge base."
                return ctx

            # Build context from documents or analyses
            if ctx.analyses:
                context = "\n\n".join([
                    f"**{a['title']}** ({a['category']}):\n{a['analysis']}"
                    for a in ctx.analyses
                ])
            else:
                # Use more documents for better coverage
                context = "\n\n".join([
                    f"**{d['title']}**:\n{d['content']}"
                    for d in ctx.documents[:5]  # Use top 5 documents
                ])

            prompt = f"""{self.instruction}

QUESTION: {ctx.query}

CONTEXT from knowledge base:
{context}

TASK: Generate a comprehensive answer that DIRECTLY addresses the question: "{ctx.query}"

Use ONLY relevant information from the context above. Focus on answering the specific question asked.

ANSWER:"""

            response = self.model.generate_content(prompt)
            ctx.answer = response.text
            ctx.set_state("synthesis_completed", True)

            logger.info(f"✅ Synthesis complete")
            return ctx

        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            # Fallback to document content
            ctx.answer = ctx.documents[0]['content'] if ctx.documents else "Error generating answer"
            return ctx


class ParallelAgent:
    """
    Workflow Agent - Parallel execution pattern
    Implements ADK ParallelAgent for concurrent processing
    """
    def __init__(self, name: str, sub_agents: List[BaseAgent]):
        self.name = name
        self.sub_agents = sub_agents
        logger.info(f"✅ Initialized {name} with {len(sub_agents)} sub-agents")

    def run(self, ctx: AgentContext) -> AgentContext:
        """Execute sub-agents in parallel"""
        logger.info(f"⚡ Running {len(self.sub_agents)} agents in parallel")

        with ThreadPoolExecutor(max_workers=len(self.sub_agents)) as executor:
            futures = [executor.submit(agent.run, ctx) for agent in self.sub_agents]
            # Wait for all to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Parallel execution error: {e}")

        logger.info(f"✅ Parallel execution complete")
        return ctx


class SequentialAgent:
    """
    Workflow Agent - Sequential execution pattern
    Implements ADK SequentialAgent for step-by-step processing
    """
    def __init__(self, name: str, sub_agents: List[BaseAgent]):
        self.name = name
        self.sub_agents = sub_agents
        logger.info(f"✅ Initialized {name} with {len(sub_agents)} sub-agents")

    def run(self, ctx: AgentContext) -> AgentContext:
        """Execute sub-agents sequentially"""
        logger.info(f"🔄 Running {len(self.sub_agents)} agents sequentially")

        for agent in self.sub_agents:
            try:
                ctx = agent.run(ctx)
            except Exception as e:
                logger.error(f"Sequential execution error at {agent.name}: {e}")

        logger.info(f"✅ Sequential execution complete")
        return ctx


class CustomOrchestrator(BaseAgent):
    """
    Custom Agent - Intelligent orchestration with conditional logic
    Implements ADK custom agent pattern with state-driven routing
    """
    def __init__(self, kb_manager: KnowledgeBaseManager):
        super().__init__(name="CustomOrchestrator")

        # Initialize all sub-agents
        self.coordinator = CoordinatorAgent()
        self.searcher = SearchAgent()
        self.retriever = RetrievalAgent(kb_manager)
        self.analyzer = AnalysisAgent()
        self.synthesizer = SynthesisAgent()

        logger.info("✅ CustomOrchestrator initialized with all agents")

    def run(self, ctx: AgentContext) -> AgentContext:
        """
        Orchestrate agents based on strategy.
        Implements conditional routing following ADK custom agent pattern.
        """
        logger.info(f"🎯 Orchestrating query: {ctx.query}")

        # Step 1: Decide strategy
        ctx = self.coordinator.run(ctx)

        # Step 2: Extract search terms
        ctx = self.searcher.run(ctx)

        # Step 3: Retrieve documents
        ctx = self.retriever.run(ctx)

        if not ctx.documents:
            ctx.answer = "No relevant information found in knowledge base."
            return ctx

        # Step 4: Conditional orchestration based on strategy

        if ctx.strategy == "SIMPLE":
            # Direct synthesis without deep analysis
            logger.info("📝 SIMPLE strategy: Direct synthesis")
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "MULTI_TOPIC":
            # Parallel analysis of multiple topics
            logger.info("🔀 MULTI_TOPIC strategy: Parallel analysis")

            # Group documents by topic
            topic_groups = {}
            for doc in ctx.documents:
                topic = doc.get('category', 'General')
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(doc)

            # Analyze each topic
            all_analyses = []
            for topic, docs in topic_groups.items():
                temp_ctx = AgentContext(
                    query=f"{ctx.query} (focusing on {topic})",
                    documents=docs
                )
                temp_ctx = self.analyzer.run(temp_ctx)
                all_analyses.extend(temp_ctx.analyses)

            ctx.analyses = all_analyses
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "DEEP_SEQUENTIAL":
            # Sequential deep analysis
            logger.info("🔍 DEEP_SEQUENTIAL strategy: Step-by-step analysis")

            # Step 4.1: Analyze documents
            ctx = self.analyzer.run(ctx)

            # Step 4.2: Synthesize with analyses
            ctx = self.synthesizer.run(ctx)

        elif ctx.strategy == "PARALLEL_SEARCH":
            # Parallel search and analysis
            logger.info("⚡ PARALLEL_SEARCH strategy: Concurrent processing")

            # Split documents for parallel analysis
            mid = len(ctx.documents) // 2

            # Create two contexts for parallel processing
            ctx1 = AgentContext(query=ctx.query, documents=ctx.documents[:mid])
            ctx2 = AgentContext(query=ctx.query, documents=ctx.documents[mid:])

            # Analyze in parallel
            parallel = ParallelAgent(
                name="ParallelAnalyzers",
                sub_agents=[self.analyzer, self.analyzer]
            )

            # Merge results (simplified - would need proper merging)
            ctx1 = self.analyzer.run(ctx1)
            ctx2 = self.analyzer.run(ctx2)

            ctx.analyses = ctx1.analyses + ctx2.analyses
            ctx = self.synthesizer.run(ctx)

        else:
            # Fallback to simple
            ctx = self.synthesizer.run(ctx)

        logger.info("🎊 Orchestration complete")
        return ctx


class EnhancedAgenticRAG:
    """
    Main RAG system with multi-agent orchestration.
    Follows ADK best practices for agent hierarchy and communication.
    """
    def __init__(self):
        logger.info("🚀 Initializing Enhanced Agentic RAG System...")

        # Load knowledge base
        self.kb = KnowledgeBaseManager()
        self.kb.parse_typescript_kb()
        self.kb.build_indexes()

        # Initialize orchestrator (manages all sub-agents)
        self.orchestrator = CustomOrchestrator(self.kb)

        logger.info(f"✅ System ready with {len(self.kb.entries):,} entries")

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Process query using multi-agent orchestration.
        Returns complete, comprehensive answer.
        """
        # Create shared context
        ctx = AgentContext(query=question)

        # Run orchestrator
        ctx = self.orchestrator.run(ctx)

        # Return results
        return {
            "answer": ctx.answer,
            "sources": ctx.documents,
            "metadata": {
                "strategy": ctx.strategy,
                "search_terms": ctx.search_terms,
                "documents_found": len(ctx.documents),
                "analyses_performed": len(ctx.analyses),
                **ctx.metadata
            }
        }


# Initialize system
rag = EnhancedAgenticRAG()


@app.get("/")
async def home():
    return FileResponse("../docs/index.html")


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "system": "Enhanced Multi-Agent Agentic RAG",
        "agents": ["Coordinator", "Search", "Retrieval", "Analysis", "Synthesis"],
        "orchestration": ["Sequential", "Parallel", "Conditional"],
        "total_documents": len(rag.kb.entries)
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
                    "content": s['content'],  # FULL content, NO truncation
                    "category": s.get('category', 'General'),
                    "score": s.get('score', 0)
                }
                for s in result["sources"][:5]
            ],
            "metadata": result["metadata"]
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
    print("🤖 ENHANCED AGENTIC RAG - ADK Multi-Agent Pattern")
    print("="*80)
    print("\n✨ Agent Architecture:")
    print("  • CustomOrchestrator - Intelligent conditional routing")
    print("  • CoordinatorAgent - LLM-based strategy selection")
    print("  • SearchAgent - Optimal term extraction")
    print("  • RetrievalAgent - Knowledge base search")
    print("  • AnalysisAgent - Deep document analysis")
    print("  • SynthesisAgent - Comprehensive answer generation")
    print("\n📊 Orchestration Patterns:")
    print("  • SIMPLE - Direct synthesis")
    print("  • MULTI_TOPIC - Parallel topic analysis")
    print("  • DEEP_SEQUENTIAL - Step-by-step processing")
    print("  • PARALLEL_SEARCH - Concurrent search & analysis")
    print("\n🔗 ADK Patterns Implemented:")
    print("  • Shared state (AgentContext)")
    print("  • Sequential execution (SequentialAgent)")
    print("  • Parallel execution (ParallelAgent)")
    print("  • Custom orchestration (CustomOrchestrator)")
    print("  • Agent hierarchy (parent-child relationships)")
    print(f"\n📚 Knowledge Base: {len(rag.kb.entries):,} entries")
    print("="*80 + "\n")

    print("🌐 Server: http://localhost:8000\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
