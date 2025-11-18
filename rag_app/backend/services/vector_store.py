"""Vector database service using ChromaDB."""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreService:
    """Manages the vector database for RAG."""

    def __init__(self):
        """Initialize the vector store service."""
        self.persist_directory = settings.chroma_persist_directory
        self.collection_name = settings.collection_name

        # Initialize embeddings model
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        logger.info("This may take a while as the model needs to be downloaded...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("Embedding model loaded successfully.")

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Initialize ChromaDB
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load the ChromaDB vectorstore."""
        try:
            logger.info(f"Initializing ChromaDB at {self.persist_directory}")

            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )

            logger.info("ChromaDB initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def add_documents(self, articles: List[Dict[str, Any]]) -> int:
        """
        Add articles to the vector database.

        Args:
            articles: List of article dictionaries

        Returns:
            Number of documents added
        """
        try:
            if not articles:
                logger.warning("No articles to add")
                return 0

            # Convert articles to LangChain Documents
            documents = []
            for article in articles:
                content = f"Title: {article['title']}\n\n{article['content']}"

                doc = Document(
                    page_content=content,
                    metadata={
                        "title": article["title"],
                        "url": article["url"],
                        "source": article["source"],
                        "category": article["category"],
                        "published_date": article.get("published_date", ""),
                        "fetched_date": article.get("fetched_date", "")
                    }
                )
                documents.append(doc)

            # Split documents into chunks
            logger.info(f"Splitting {len(documents)} documents into chunks")
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(split_docs)} chunks")

            # Add to vectorstore
            logger.info("Adding documents to ChromaDB")
            self.vectorstore.add_documents(split_docs)

            logger.info(f"Successfully added {len(split_docs)} document chunks")
            return len(split_docs)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            if k is None:
                k = settings.top_k_results

            logger.info(f"Searching for: {query}")

            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(query, k=k)

            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })

            logger.info(f"Found {len(formatted_results)} relevant documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        try:
            # Get collection
            client = chromadb.PersistentClient(path=self.persist_directory)
            collection = client.get_collection(name=self.collection_name)

            count = collection.count()

            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_model": settings.embedding_model
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": self.collection_name,
                "embedding_model": settings.embedding_model,
                "error": str(e)
            }

    def clear_database(self):
        """Clear all documents from the database."""
        try:
            logger.warning("Clearing all documents from database")

            # Reinitialize the vectorstore
            client = chromadb.PersistentClient(path=self.persist_directory)
            client.delete_collection(name=self.collection_name)

            # Reinitialize
            self._initialize_vectorstore()

            logger.info("Database cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise


# Singleton instance
_vector_store_instance: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Get or create the vector store singleton."""
    global _vector_store_instance

    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()

    return _vector_store_instance
