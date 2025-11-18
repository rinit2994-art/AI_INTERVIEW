"""Google ADK agents for intelligent RAG operations."""
import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import Tool
from config.settings import settings
from backend.services.vector_store import get_vector_store
from backend.services.rag_pipeline import get_rag_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define custom tools for agents
def search_knowledge_base(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search the knowledge base for relevant articles.

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        Dictionary with search results
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.search(query, k=top_k)

        return {
            "success": True,
            "query": query,
            "num_results": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_detailed_answer(question: str) -> Dict[str, Any]:
    """
    Get a detailed answer to a question using RAG.

    Args:
        question: User's question

    Returns:
        Dictionary with answer and sources
    """
    try:
        rag_pipeline = get_rag_pipeline()
        result = rag_pipeline.answer_question(question)

        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting answer: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Get statistics about the knowledge base.

    Returns:
        Dictionary with database statistics
    """
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()

        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Create ADK Tools
search_tool = Tool(
    name="search_knowledge_base",
    description="Search the AI/ML knowledge base for relevant articles and papers",
    func=search_knowledge_base
)

answer_tool = Tool(
    name="get_detailed_answer",
    description="Get a comprehensive answer to a question using RAG with citations",
    func=get_detailed_answer
)

stats_tool = Tool(
    name="get_knowledge_base_stats",
    description="Get statistics about the knowledge base (number of documents, etc.)",
    func=get_knowledge_base_stats
)


class ADKAgentSystem:
    """Agentic AI system using Google ADK."""

    def __init__(self):
        """Initialize the ADK agent system."""
        logger.info("Initializing ADK Agent System")

        # Create search agent
        self.search_agent = Agent(
            name="search_specialist",
            model=settings.gemini_model,
            instruction="""You are a search specialist for AI/ML content.
            Your job is to find the most relevant articles, papers, and resources
            from the knowledge base based on user queries.
            Always provide clear, concise results with relevance scores.""",
            description="Specialized agent for searching the knowledge base",
            tools=[search_tool, stats_tool]
        )

        # Create answer agent
        self.answer_agent = Agent(
            name="answer_specialist",
            model=settings.gemini_model,
            instruction="""You are an AI/ML expert assistant.
            You provide comprehensive, well-researched answers to questions about
            artificial intelligence, machine learning, data science, and generative AI.
            Always cite your sources and provide practical insights.
            If information is not in the knowledge base, acknowledge this clearly.""",
            description="Specialized agent for answering questions with RAG",
            tools=[answer_tool, search_tool]
        )

        # Create coordinator agent
        self.coordinator_agent = Agent(
            name="coordinator",
            model=settings.gemini_model,
            instruction="""You are a coordinator agent that helps users interact with
            the AI/ML knowledge base system.

            You have two specialized sub-agents:
            1. search_specialist - For finding relevant articles and papers
            2. answer_specialist - For generating detailed answers with citations

            When users:
            - Want to search or browse: Use search_specialist
            - Ask questions requiring detailed answers: Use answer_specialist
            - Need general help: Provide guidance directly

            Always be helpful, clear, and guide users to get the best results.""",
            description="Main coordinator for the RAG system",
            sub_agents=[self.search_agent, self.answer_agent]
        )

        logger.info("ADK Agent System initialized successfully")

    async def process_query(self, query: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Process a user query using the appropriate agent.

        Args:
            query: User's query
            mode: Mode of operation ('search', 'answer', or 'auto')

        Returns:
            Response from the agent
        """
        try:
            if mode == "search":
                # Direct search
                result = search_knowledge_base(query)
                return {
                    "mode": "search",
                    "result": result
                }

            elif mode == "answer":
                # Direct answer with RAG
                result = get_detailed_answer(query)
                return {
                    "mode": "answer",
                    "result": result
                }

            else:
                # Auto mode - let coordinator decide
                # Use the coordinator agent to handle the query
                response = self.coordinator_agent.run(query)

                return {
                    "mode": "auto",
                    "agent_used": "coordinator",
                    "response": response
                }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": str(e),
                "success": False
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return get_knowledge_base_stats()


# Singleton instance
_adk_agent_system: ADKAgentSystem = None


def get_adk_agent_system() -> ADKAgentSystem:
    """Get or create the ADK agent system singleton."""
    global _adk_agent_system

    if _adk_agent_system is None:
        _adk_agent_system = ADKAgentSystem()

    return _adk_agent_system
