"""
Ultimate Knowledge Expansion Pipeline
Google ADK's google_search Tool + LangChain + ChromaDB

This is the BEST expansion pipeline combining:
- Google ADK's built-in google_search tool (highest quality search)
- LangChain document processing (WebBaseLoader, text splitting)
- ChromaDB vector storage
- Parallel processing for speed
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Google ADK imports
from google.adk.tools import google_search
from google.adk.agents import Agent
from google import genai

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain.schema import Document

# ChromaDB
import chromadb
from chromadb.config import Settings

# Knowledge base
from knowledge_base_manager_v2 import KnowledgeBaseManager

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UltimateADKLangChainPipeline:
    """
    The ULTIMATE knowledge expansion pipeline.

    Features:
    - Google ADK's google_search tool (best search quality)
    - LangChain WebBaseLoader (robust web scraping)
    - LangChain RecursiveCharacterTextSplitter (optimal chunking)
    - ChromaDB with vector embeddings
    - Parallel processing
    - Automatic deduplication
    """

    def __init__(
        self,
        gemini_api_key: str,
        chroma_path: str = "./chroma_ultimate",
        max_workers: int = 5
    ):
        """
        Initialize the ultimate pipeline.

        Args:
            gemini_api_key: Gemini API key for Google ADK
            chroma_path: Path to ChromaDB storage
            max_workers: Number of parallel workers
        """
        self.max_workers = max_workers

        # Initialize Google ADK client
        self.client = genai.Client(api_key=gemini_api_key)

        # Create ADK Agent with google_search tool
        self.search_agent = Agent(
            name="search_specialist",
            model="gemini-2.0-flash-exp",
            tools=[google_search],
            instruction="""You are a search specialist. When given a topic, use the google_search
            tool to find the most relevant and high-quality web pages about that topic.
            Return the URLs of the best sources you find."""
        )

        logger.info("✅ Google ADK Agent configured with google_search tool")

        # Knowledge base manager
        self.kb_manager = KnowledgeBaseManager()

        # LangChain text splitter for optimal chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # ChromaDB setup
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            persist_directory=chroma_path
        ))

        self.collection = self.chroma_client.get_or_create_collection(
            name="ultimate_knowledge_base",
            metadata={
                "description": "Ultimate KB - Google ADK + LangChain",
                "hnsw:space": "cosine"
            }
        )

        logger.info(f"📊 Current ChromaDB size: {self.collection.count():,} chunks")

        # Tracking
        self.seen_urls = set()
        self.seen_content_hashes = set()
        self.processed_topics = set()
        self.total_documents_added = 0

    def extract_topics(self) -> List[Dict[str, Any]]:
        """Extract all topics from knowledge base with metadata."""
        logger.info("📋 Extracting topics from knowledge base...")

        self.kb_manager.parse_typescript_kb()
        self.kb_manager.build_indexes()

        topics_data = []

        # Get unique topics with priority scoring
        topic_priority = {}

        for entry in self.kb_manager.entries:
            title = entry['title']
            category = entry.get('category', 'General')
            keywords = entry.get('keywords', [])

            if title not in topic_priority:
                # Priority based on keyword count
                priority = len(keywords)
                topic_priority[title] = {
                    'topic': title,
                    'category': category,
                    'priority': priority,
                    'keywords': keywords[:5],
                    'existing_content': entry.get('content', '')[:500]
                }

        # Add high-frequency keywords as topics
        for keyword, entries in self.kb_manager.keyword_index.items():
            if len(entries) >= 5 and len(keyword) > 3:
                if keyword not in topic_priority:
                    topic_priority[keyword] = {
                        'topic': keyword,
                        'category': 'Derived',
                        'priority': len(entries),
                        'keywords': [keyword],
                        'existing_content': ''
                    }

        # Sort by priority (most important topics first)
        topics_data = sorted(
            topic_priority.values(),
            key=lambda x: x['priority'],
            reverse=True
        )

        logger.info(f"✅ Extracted {len(topics_data)} topics")
        return topics_data

    def search_with_adk(self, topic: str) -> List[str]:
        """
        Use Google ADK's google_search tool to find URLs.

        This is the BEST search because it uses Google's official ADK tool.
        """
        urls = []

        try:
            # Enhanced search query for AI/ML content
            search_query = f"{topic} AI ML tutorial explanation guide"

            # Use ADK Agent with google_search tool
            prompt = f"""Use google_search to find the top 10 most relevant and high-quality
            web pages about: {search_query}

            Focus on:
            - Official documentation
            - Tutorial sites (Towards Data Science, Medium, etc.)
            - Research papers (arXiv)
            - Technical blogs
            - Educational resources

            Return the URLs you find, one per line."""

            response = self.client.agentic.generate_text(
                model="gemini-2.0-flash-exp",
                prompt=prompt,
                agent=self.search_agent
            )

            # Extract URLs from response
            if response and response.text:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    # Extract URL if line contains http/https
                    if 'http://' in line or 'https://' in line:
                        # Simple URL extraction
                        if line.startswith('http'):
                            urls.append(line)
                        else:
                            # Extract URL from text
                            import re
                            url_match = re.search(r'https?://[^\s]+', line)
                            if url_match:
                                urls.append(url_match.group(0))

            logger.info(f"  ✓ Google ADK Search: Found {len(urls)} URLs for '{topic[:50]}'")

        except Exception as e:
            logger.error(f"  ✗ Google ADK Search error: {e}")

        return urls

    def scrape_and_chunk_url(self, url: str, topic: str) -> List[Document]:
        """
        Scrape URL using LangChain WebBaseLoader and split into chunks.

        This is BETTER than basic scraping because:
        - LangChain handles various HTML structures
        - Robust error handling
        - Optimal text extraction
        """
        # Check if already processed
        if url in self.seen_urls:
            return []

        chunks = []

        try:
            # Use LangChain WebBaseLoader for robust scraping
            loader = WebBaseLoader(url)
            loader.requests_kwargs = {'timeout': 10}

            documents = loader.load()

            # Split into optimal chunks using LangChain
            splits = self.text_splitter.split_documents(documents)

            # Add metadata
            for split in splits:
                split.metadata['topic'] = topic
                split.metadata['source_url'] = url
                chunks.append(split)

            self.seen_urls.add(url)
            logger.info(f"  ✓ Scraped: {url[:60]}... → {len(chunks)} chunks")

        except Exception as e:
            logger.debug(f"  ✗ Failed to scrape {url}: {e}")

        return chunks

    def add_chunks_to_chromadb(self, chunks: List[Document], topic_data: Dict) -> int:
        """Add document chunks to ChromaDB with deduplication."""
        if not chunks:
            return 0

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            content = chunk.page_content

            # Skip very short chunks
            if len(content) < 100:
                continue

            # Deduplication using content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()

            if content_hash in self.seen_content_hashes:
                continue

            self.seen_content_hashes.add(content_hash)

            # Prepare for ChromaDB
            documents.append(content)
            metadatas.append({
                'topic': topic_data['topic'],
                'category': topic_data['category'],
                'source_url': chunk.metadata.get('source_url', ''),
                'keywords': ','.join(topic_data['keywords'][:5])
            })
            ids.append(content_hash)

        # Batch add to ChromaDB
        if documents:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                return len(documents)
            except Exception as e:
                logger.error(f"Error adding to ChromaDB: {e}")
                return 0

        return 0

    def process_topic(self, topic_data: Dict[str, Any]) -> int:
        """
        Process a single topic using the ULTIMATE pipeline:
        1. Google ADK search (best URLs)
        2. LangChain scraping (robust extraction)
        3. LangChain chunking (optimal splits)
        4. ChromaDB storage (vector embeddings)
        """
        topic = topic_data['topic']

        if topic in self.processed_topics:
            return 0

        logger.info(f"🔍 Processing: {topic}")

        # Step 1: Get URLs using Google ADK's google_search tool
        urls = self.search_with_adk(topic)

        if not urls:
            logger.warning(f"  ⚠️  No URLs found for '{topic}'")
            self.processed_topics.add(topic)
            return 0

        # Step 2: Scrape and chunk using LangChain
        all_chunks = []
        for url in urls[:8]:  # Process top 8 URLs for quality
            chunks = self.scrape_and_chunk_url(url, topic)
            all_chunks.extend(chunks)
            time.sleep(0.5)  # Be polite

        # Step 3: Add to ChromaDB
        added = self.add_chunks_to_chromadb(all_chunks, topic_data)

        self.processed_topics.add(topic)
        self.total_documents_added += added

        logger.info(f"  ✅ Added {added} chunks for '{topic}' | Total: {self.collection.count():,}")

        return added

    def run_pipeline(self, max_topics: int = None, parallel: bool = True):
        """Run the ULTIMATE expansion pipeline."""
        logger.info("\n" + "="*80)
        logger.info("🚀 ULTIMATE EXPANSION PIPELINE")
        logger.info("   Google ADK google_search + LangChain + ChromaDB")
        logger.info("="*80)
        logger.info(f"  Search: Google ADK's google_search tool (BEST quality)")
        logger.info(f"  Scraping: LangChain WebBaseLoader (robust)")
        logger.info(f"  Chunking: LangChain RecursiveCharacterTextSplitter (optimal)")
        logger.info(f"  Storage: ChromaDB with vector embeddings")
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
        logger.info(f"✅ ULTIMATE PIPELINE COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"  Topics processed: {len(self.processed_topics)}")
        logger.info(f"  Chunks added: {self.total_documents_added:,}")
        logger.info(f"  Final KB size: {self.collection.count():,}")
        logger.info(f"  Unique URLs scraped: {len(self.seen_urls)}")
        logger.info(f"  Unique content pieces: {len(self.seen_content_hashes):,}")
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
            'unique_content': len(self.seen_content_hashes),
            'documents_added': self.total_documents_added,
            'search_tool': 'Google ADK google_search (BEST)'
        }


def main():
    """Main execution with configuration."""
    print("\n" + "="*80)
    print("🚀 ULTIMATE KNOWLEDGE EXPANSION PIPELINE")
    print("   Google ADK google_search + LangChain + ChromaDB")
    print("="*80)
    print("\n🌟 This is the BEST expansion pipeline!")
    print("\nFeatures:")
    print("  ✅ Google ADK's google_search tool - Highest quality search results")
    print("  ✅ LangChain WebBaseLoader - Robust web scraping")
    print("  ✅ LangChain RecursiveCharacterTextSplitter - Optimal chunking")
    print("  ✅ ChromaDB - Vector embeddings and storage")
    print("  ✅ Parallel processing - 5x faster")
    print("  ✅ Automatic deduplication - No duplicates")
    print("\n" + "="*80)

    # Configuration
    GEMINI_API_KEY = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"

    # Pipeline settings
    MAX_TOPICS = 50   # Set to None for ALL topics
    MAX_WORKERS = 5   # Parallel workers
    PARALLEL = True   # Use parallel processing

    print(f"\n📋 Pipeline Settings:")
    print(f"  API Key: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-10:]}")
    print(f"  Max topics: {MAX_TOPICS if MAX_TOPICS else 'ALL'}")
    print(f"  Workers: {MAX_WORKERS if PARALLEL else 1}")
    print(f"  Mode: {'Parallel' if PARALLEL else 'Sequential'}")
    print("\n" + "="*80 + "\n")

    input("Press Enter to start the ULTIMATE pipeline...")

    # Initialize and run
    pipeline = UltimateADKLangChainPipeline(
        gemini_api_key=GEMINI_API_KEY,
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
        print(f"  Unique content pieces: {stats['unique_content']:,}")
        print(f"  Search tool: {stats['search_tool']}")
        print("\n✅ LARGEST KNOWLEDGE BASE CREATED!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
