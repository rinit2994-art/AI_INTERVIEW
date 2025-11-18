"""
ChromaDB Manager with Best Embedding Model
Persistent storage with sentence-transformers
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict, Any
import hashlib
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Manages ChromaDB with persistent storage and best embedding model
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB with sentence-transformers embedding

        Using 'all-mpnet-base-v2' - Best quality embedding model:
        - 768 dimensions
        - SOTA performance on semantic search
        - Based on MPNet architecture
        """
        logger.info("🚀 Initializing ChromaDB with all-mpnet-base-v2 embedding model...")

        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Use sentence-transformers embedding function
        # all-mpnet-base-v2: Best quality (768-dim)
        # Alternative: all-MiniLM-L6-v2 (384-dim, faster)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )

        # Create or get collection
        self.collection_name = "web_content"
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ Loaded existing collection: {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Web content from continuous pipeline"}
            )
            logger.info("✅ Created new collection")

        logger.info(f"📁 Persistent storage: {persist_directory}")
        logger.info(f"🧠 Embedding model: all-mpnet-base-v2 (768-dim)")

    def generate_id(self, content: str, url: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(f"{url}:{content[:100]}".encode()).hexdigest()

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to ChromaDB

        Args:
            documents: List of dicts with keys: content, metadata (url, source, title, etc.)

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        ids = []
        contents = []
        metadatas = []

        for doc in documents:
            content = doc.get('content', '')
            url = doc.get('metadata', {}).get('url', '')

            if not content or len(content) < 50:
                continue

            doc_id = self.generate_id(content, url)

            # Check if already exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    logger.debug(f"⏭️  Skipping duplicate: {url}")
                    continue
            except:
                pass

            ids.append(doc_id)
            contents.append(content)

            # Add timestamp
            metadata = doc.get('metadata', {})
            metadata['added_at'] = datetime.utcnow().isoformat()
            metadatas.append(metadata)

        if not ids:
            return 0

        try:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            logger.info(f"✅ Added {len(ids)} documents to ChromaDB")
            return len(ids)

        except Exception as e:
            logger.error(f"❌ Error adding documents: {e}")
            return 0

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Query ChromaDB with semantic search

        Args:
            query_text: Search query
            n_results: Number of results to return

        Returns:
            Query results with documents, distances, metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )

            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'distances': results['distances'][0] if results['distances'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'ids': results['ids'][0] if results['ids'] else []
            }

        except Exception as e:
            logger.error(f"❌ Query error: {e}")
            return {'documents': [], 'distances': [], 'metadatas': [], 'ids': []}

    def count(self) -> int:
        """Get total document count"""
        return self.collection.count()

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        count = self.count()

        # Get sample to analyze sources
        sample = self.collection.get(limit=min(100, count))
        sources = {}

        if sample['metadatas']:
            for meta in sample['metadatas']:
                source = meta.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1

        return {
            'total_documents': count,
            'sources': sources,
            'embedding_model': 'all-mpnet-base-v2',
            'embedding_dimension': 768
        }

    def reset(self):
        """Reset collection (delete all data)"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        logger.info("🗑️  Collection reset")


if __name__ == "__main__":
    # Test ChromaDB setup
    print("\n" + "="*80)
    print("🧪 Testing ChromaDB Manager")
    print("="*80 + "\n")

    manager = ChromaDBManager()

    # Test add
    test_docs = [
        {
            'content': 'ChromaDB is an open-source embedding database that makes it easy to build LLM applications.',
            'metadata': {
                'url': 'https://example.com/chroma',
                'source': 'test',
                'title': 'ChromaDB Introduction'
            }
        },
        {
            'content': 'Vector databases store embeddings and enable semantic search over unstructured data.',
            'metadata': {
                'url': 'https://example.com/vectors',
                'source': 'test',
                'title': 'Vector Databases'
            }
        }
    ]

    added = manager.add_documents(test_docs)
    print(f"✅ Added {added} test documents\n")

    # Test query
    results = manager.query("What is ChromaDB?", n_results=2)
    print("🔍 Query results:")
    for i, (doc, dist) in enumerate(zip(results['documents'], results['distances'])):
        print(f"\n  {i+1}. Distance: {dist:.4f}")
        print(f"     Content: {doc[:100]}...")

    # Stats
    print("\n📊 Stats:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*80)
