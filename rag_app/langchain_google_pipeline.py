"""
Ultimate Knowledge Expansion Pipeline
Using LangChain + Google Search API + Advanced RAG
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.docstore.document import Document
from langchain.schema import Document as LCDocument

# ChromaDB
import chromadb
from chromadb.config import Settings

# Knowledge base
from knowledge_base_manager_v2 import KnowledgeBaseManager

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangChainGooglePipeline:
    """
    Ultimate knowledge expansion using LangChain + Google Search.

    Features:
    - Google Custom Search API for high-quality results
    - LangChain document loaders for web scraping
    - Advanced text splitting for optimal chunks
    - ChromaDB with embeddings
    - Parallel processing
    """

    def __init__(
        self,
        google_api_key: str = None,
        google_cse_id: str = None,
        chroma_path: str = "./chroma_langchain",
        max_workers: int = 5
    ):
        """
        Initialize the pipeline.

        Args:
            google_api_key: Google API key for Custom Search
            google_cse_id: Google Custom Search Engine ID
            chroma_path: Path to ChromaDB storage
            max_workers: Number of parallel workers
        """
        self.max_workers = max_workers

        # Google Search setup
        if google_api_key and google_cse_id:
            os.environ["GOOGLE_API_KEY"] = google_api_key
            os.environ["GOOGLE_CSE_ID"] = google_cse_id
            self.google_search = GoogleSearchAPIWrapper()
            logger.info("✅ Google Search API configured")
        else:
            self.google_search = None
            logger.warning("⚠️  No Google API credentials - using fallback search")

        # Knowledge base manager
        self.kb_manager = KnowledgeBaseManager()

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # ChromaDB setup
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            persist_directory=chroma_path
        ))

        self.collection = self.chroma_client.get_or_create_collection(
            name="langchain_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"📊 Current ChromaDB size: {self.collection.count():,} chunks")

        # Tracking
        self.seen_urls = set()
        self.processed_topics = set()
        self.total_documents_added = 0

    def extract_topics(self) -> List[Dict[str, Any]]:
        """Extract all topics from knowledge base."""
        logger.info("📋 Extracting topics from knowledge base...")

        self.kb_manager.parse_typescript_kb()
        self.kb_manager.build_indexes()

        topics_data = []

        # Get unique topics with metadata
        for entry in self.kb_manager.entries:
            topics_data.append({
                'topic': entry['title'],
                'category': entry.get('category', 'General'),
                'keywords': entry.get('keywords', [])[:5],
                'existing_content': entry.get('content', '')[:500]  # Preview
            })

        # Add high-frequency keywords as topics
        for keyword, entries in self.kb_manager.keyword_index.items():
            if len(entries) >= 5 and len(keyword) > 3:  # Frequent, meaningful keywords
                topics_data.append({
                    'topic': keyword,
                    'category': 'Derived',
                    'keywords': [keyword],
                    'existing_content': ''
                })

        logger.info(f"✅ Extracted {len(topics_data)} topics")
        return topics_data

    def google_search_urls(self, query: str, num_results: int = 10) -> List[str]:
        """Search Google and return URLs."""
        urls = []

        if self.google_search:
            try:
                # Use Google Search API
                results = self.google_search.results(query, num_results=num_results)
                urls = [r.get('link', '') for r in results if 'link' in r]
                logger.info(f"  ✓ Google Search: Found {len(urls)} URLs for '{query[:50]}'")
            except Exception as e:
                logger.error(f"  ✗ Google Search error: {e}")

        # Fallback: DuckDuckGo
        if not urls:
            urls = self._fallback_search(query, num_results)

        return urls

    def _fallback_search(self, query: str, num_results: int = 10) -> List[str]:
        """Fallback search using DuckDuckGo."""
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import quote_plus

        urls = []
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            for result in soup.find_all('div', class_='result')[:num_results]:
                link = result.find('a', class_='result__a')
                if link and link.get('href'):
                    urls.append(link['href'])

            logger.info(f"  ✓ Fallback Search: Found {len(urls)} URLs")
        except Exception as e:
            logger.error(f"  ✗ Fallback search error: {e}")

        return urls

    def scrape_and_chunk_url(self, url: str, topic: str) -> List[Document]:
        """Scrape URL and split into chunks using LangChain."""
        # Check if already processed
        if url in self.seen_urls:
            return []

        chunks = []

        try:
            # Use LangChain WebBaseLoader
            loader = WebBaseLoader(url)
            documents = loader.load()

            # Split into chunks
            splits = self.text_splitter.split_documents(documents)

            # Add metadata
            for split in splits:
                split.metadata['topic'] = topic
                split.metadata['source_url'] = url
                chunks.append(split)

            self.seen_urls.add(url)
            logger.info(f"  ✓ Scraped: {url[:50]}... → {len(chunks)} chunks")

        except Exception as e:
            logger.debug(f"  ✗ Failed to scrape {url}: {e}")

        return chunks

    def process_topic(self, topic_data: Dict[str, Any]) -> int:
        """Process a single topic: search → scrape → chunk → store."""
        topic = topic_data['topic']

        if topic in self.processed_topics:
            return 0

        logger.info(f"🔍 Processing: {topic}")

        # Enhanced search query
        search_query = f"{topic} AI ML tutorial explanation"

        # Get URLs from Google Search
        urls = self.google_search_urls(search_query, num_results=10)

        if not urls:
            logger.warning(f"  ⚠️  No URLs found for '{topic}'")
            self.processed_topics.add(topic)
            return 0

        # Scrape and chunk all URLs
        all_chunks = []
        for url in urls[:5]:  # Limit to top 5 for quality
            chunks = self.scrape_and_chunk_url(url, topic)
            all_chunks.extend(chunks)
            time.sleep(0.5)  # Be polite

        # Add to ChromaDB
        added = self.add_chunks_to_chromadb(all_chunks, topic_data)

        self.processed_topics.add(topic)
        self.total_documents_added += added

        logger.info(f"  ✅ Added {added} chunks for '{topic}' | Total: {self.collection.count():,}")

        return added

    def add_chunks_to_chromadb(self, chunks: List[Document], topic_data: Dict) -> int:
        """Add document chunks to ChromaDB."""
        if not chunks:
            return 0

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            # Create unique ID
            content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()
            chunk_id = f"{topic_data['topic']}_{content_hash}"

            # Prepare for ChromaDB
            documents.append(chunk.page_content)
            metadatas.append({
                'topic': topic_data['topic'],
                'category': topic_data['category'],
                'source_url': chunk.metadata.get('source_url', ''),
                'keywords': ','.join(topic_data['keywords'][:5])
            })
            ids.append(chunk_id)

        try:
            # Add to ChromaDB (it will generate embeddings)
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return len(documents)
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            return 0

    def run_pipeline(self, max_topics: int = None, parallel: bool = True):
        """Run the complete pipeline."""
        logger.info("\n" + "="*80)
        logger.info("🚀 LANGCHAIN + GOOGLE SEARCH EXPANSION PIPELINE")
        logger.info("="*80)
        logger.info(f"  Google Search: {'✅ Enabled' if self.google_search else '⚠️  Fallback'}")
        logger.info(f"  Parallel workers: {self.max_workers if parallel else 1}")
        logger.info(f"  Starting KB size: {self.collection.count():,} chunks")
        logger.info("="*80 + "\n")

        # Extract topics
        topics_data = self.extract_topics()

        if max_topics:
            topics_data = topics_data[:max_topics]

        logger.info(f"📋 Processing {len(topics_data)} topics\n")

        # Process topics
        if parallel:
            self._process_parallel(topics_data)
        else:
            self._process_sequential(topics_data)

        logger.info(f"\n{'='*80}")
        logger.info(f"✅ PIPELINE COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"  Topics processed: {len(self.processed_topics)}")
        logger.info(f"  Chunks added: {self.total_documents_added:,}")
        logger.info(f"  Final KB size: {self.collection.count():,}")
        logger.info(f"  Unique URLs: {len(self.seen_urls)}")
        logger.info(f"{'='*80}\n")

    def _process_parallel(self, topics_data: List[Dict]):
        """Process topics in parallel."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_topic = {
                executor.submit(self.process_topic, td): td
                for td in topics_data
            }

            completed = 0
            for future in as_completed(future_to_topic):
                completed += 1

                if completed % 10 == 0:
                    logger.info(f"\n📊 Progress: {completed}/{len(topics_data)} topics | "
                              f"Total chunks: {self.collection.count():,}\n")

    def _process_sequential(self, topics_data: List[Dict]):
        """Process topics sequentially."""
        for i, topic_data in enumerate(topics_data, 1):
            self.process_topic(topic_data)

            if i % 10 == 0:
                logger.info(f"\n📊 Progress: {i}/{len(topics_data)} topics | "
                          f"Total chunks: {self.collection.count():,}\n")

            time.sleep(1)  # Be polite

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'total_chunks': self.collection.count(),
            'topics_processed': len(self.processed_topics),
            'unique_urls': len(self.seen_urls),
            'documents_added': self.total_documents_added,
            'has_google_search': self.google_search is not None
        }


def main():
    """Main execution with configuration."""
    print("\n" + "="*80)
    print("🚀 ULTIMATE KNOWLEDGE EXPANSION PIPELINE")
    print("   LangChain + Google Search API + ChromaDB")
    print("="*80)

    print("\n⚙️  CONFIGURATION:")
    print("  1. Set Google API credentials (recommended)")
    print("  2. Or use fallback DuckDuckGo search")
    print("\n" + "="*80)

    # Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", None)
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", None)

    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("\n⚠️  Google API credentials not found in environment")
        print("   Using fallback search (DuckDuckGo)")
        print("\nTo use Google Search API:")
        print("  1. Get API key: https://console.cloud.google.com/apis/credentials")
        print("  2. Create Custom Search Engine: https://programmablesearchengine.google.com/")
        print("  3. Set environment variables:")
        print("     export GOOGLE_API_KEY='your-api-key'")
        print("     export GOOGLE_CSE_ID='your-cse-id'")
        print("\n" + "="*80)
    else:
        print("\n✅ Google Search API configured!")

    # Pipeline settings
    MAX_TOPICS = 50  # Set to None for ALL topics
    MAX_WORKERS = 5   # Parallel workers
    PARALLEL = True   # Use parallel processing

    print(f"\n📋 Pipeline Settings:")
    print(f"  Max topics: {MAX_TOPICS if MAX_TOPICS else 'ALL'}")
    print(f"  Workers: {MAX_WORKERS if PARALLEL else 1}")
    print(f"  Mode: {'Parallel' if PARALLEL else 'Sequential'}")
    print("\n" + "="*80 + "\n")

    input("Press Enter to start...")

    # Initialize and run
    pipeline = LangChainGooglePipeline(
        google_api_key=GOOGLE_API_KEY,
        google_cse_id=GOOGLE_CSE_ID,
        max_workers=MAX_WORKERS
    )

    try:
        pipeline.run_pipeline(max_topics=MAX_TOPICS, parallel=PARALLEL)

        # Final stats
        stats = pipeline.get_stats()
        print("\n📊 FINAL STATISTICS:")
        print(f"  Total chunks: {stats['total_chunks']:,}")
        print(f"  Topics processed: {stats['topics_processed']}")
        print(f"  Unique URLs scraped: {stats['unique_urls']}")
        print(f"  Google Search used: {'Yes' if stats['has_google_search'] else 'No (fallback)'}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
