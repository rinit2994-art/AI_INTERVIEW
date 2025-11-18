"""RAG pipeline using LangChain and Gemini."""
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config.settings import settings
from backend.services.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for answering questions using retrieved context."""

    def __init__(self):
        """Initialize the RAG pipeline."""
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens
        )

        # Get vector store
        self.vector_store = get_vector_store().vectorstore

        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI assistant specialized in Artificial Intelligence, Machine Learning, Data Science, and Generative AI.

Use the following pieces of context from recent articles, research papers, and blog posts to answer the question.
If you don't know the answer based on the context, say so. Always cite the sources when possible.

Context:
{context}

Question: {question}

Answer: Provide a comprehensive answer based on the context above. Include:
1. A clear, detailed answer
2. Key insights from the sources
3. Relevant examples or use cases mentioned
4. Citations to the sources (title and URL when available)

Answer:"""
        )

        # Create retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": settings.top_k_results}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )

        logger.info("RAG Pipeline initialized successfully")

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User's question

        Returns:
            Dictionary with answer and sources
        """
        try:
            logger.info(f"Processing question: {question}")

            # Get answer from RAG chain
            result = self.qa_chain({"query": question})

            # Extract source documents
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "title": doc.metadata.get("title", "Unknown"),
                    "url": doc.metadata.get("url", ""),
                    "source": doc.metadata.get("source", "Unknown"),
                    "category": doc.metadata.get("category", ""),
                    "content_preview": doc.page_content[:200] + "..."
                })

            response = {
                "answer": result["result"],
                "sources": sources,
                "num_sources": len(sources),
                "question": question
            }

            logger.info(f"Generated answer with {len(sources)} sources")
            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant documents without generating an answer.

        Args:
            query: Search query
            k: Number of documents to retrieve

        Returns:
            List of relevant documents
        """
        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            docs = retriever.get_relevant_documents(query)

            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

            return results

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise


# Singleton instance
_rag_pipeline_instance: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline singleton."""
    global _rag_pipeline_instance

    if _rag_pipeline_instance is None:
        _rag_pipeline_instance = RAGPipeline()

    return _rag_pipeline_instance
