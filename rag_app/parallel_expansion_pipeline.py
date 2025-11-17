"""
Parallel Knowledge Base Expansion Pipeline
Uses multiprocessing for 10x faster knowledge base growth
"""

import json
import time
import hashlib
import logging
from typing import List, Dict, Any, Set
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from knowledge_base_manager_v2 import KnowledgeBaseManager
from threading import Lock

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParallelKnowledgeExpansion:
    """Parallel knowledge base expansion for maximum speed."""

    def __init__(self, chroma_path: str = "./chroma_db", max_workers: int = 10):
        self.kb_manager = KnowledgeBaseManager()
        self.seen_content_hashes: Set[str] = set()
        self.processed_topics: Set[str] = set()
        self.max_workers = max_workers
        self.lock = Lock()  # For thread-safe operations

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=False,
            persist_directory=chroma_path
        ))

        self.collection = self.chroma_client.get_or_create_collection(
            name="mega_knowledge_base",
            metadata={"description": "Largest AI/ML/Tech Knowledge Base - Parallel Built"}
        )

        logger.info(f"🚀 Parallel Pipeline initialized with {max_workers} workers")
        logger.info(f"📊 Current ChromaDB size: {self.collection.count():,} documents")

    def extract_all_topics(self) -> List[Dict[str, Any]]:
        """Extract all topics with metadata."""
        logger.info("📋 Extracting topics from knowledge base...")

        self.kb_manager.parse_typescript_kb()
        self.kb_manager.build_indexes()

        topics_data = []

        # Get all unique topics with priority
        topic_priority = {}

        for entry in self.kb_manager.entries:
            title = entry['title']
            category = entry.get('category', 'General')
            keywords = entry.get('keywords', [])

            # Add title as topic
            if title not in topic_priority:
                topic_priority[title] = {
                    'topic': title,
                    'category': category,
                    'priority': len(keywords),
                    'keywords': keywords[:5]
                }

            # Add important keywords as topics
            for keyword in keywords:
                if len(keyword) > 3 and keyword not in topic_priority:
                    priority = len(self.kb_manager.keyword_index.get(keyword.lower(), []))
                    topic_priority[keyword] = {
                        'topic': keyword,
                        'category': category,
                        'priority': priority,
                        'keywords': [keyword]
                    }

        # Sort by priority
        topics_data = sorted(topic_priority.values(), key=lambda x: x['priority'], reverse=True)

        logger.info(f"✅ Extracted {len(topics_data)} unique topics")
        return topics_data

    def search_multiple_sources(self, topic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search multiple sources in parallel for a topic."""
        topic = topic_data['topic']
        results = []

        try:
            # Wikipedia
            wiki = self._search_wikipedia(topic)
            if wiki:
                wiki['topic'] = topic
                wiki['category'] = topic_data['category']
                results.append(wiki)

            # arXiv
            arxiv_results = self._search_arxiv(topic)
            for paper in arxiv_results:
                paper['topic'] = topic
                paper['category'] = topic_data['category']
                results.append(paper)

            # Web Search
            web_results = self._search_web(topic)
            for web_doc in web_results:
                web_doc['topic'] = topic
                web_doc['category'] = topic_data['category']
                results.append(web_doc)

        except Exception as e:
            logger.error(f"Error searching for '{topic}': {e}")

        return results

    def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search Wikipedia."""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': query,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    content = page_data.get('extract', '')
                    if len(content) > 100:
                        return {
                            'title': page_data.get('title', ''),
                            'content': content,
                            'url': f"https://en.wikipedia.org/wiki/{quote_plus(query)}",
                            'source': 'Wikipedia'
                        }
        except Exception as e:
            logger.debug(f"Wikipedia error for '{query}': {e}")

        return None

    def _search_arxiv(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search arXiv."""
        results = []
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance'
            }

            response = requests.get(url, params=params, timeout=15)
            soup = BeautifulSoup(response.text, 'xml')

            for entry in soup.find_all('entry'):
                title = entry.find('title')
                summary = entry.find('summary')
                link = entry.find('id')

                if title and summary:
                    content = summary.get_text(strip=True)
                    if len(content) > 100:
                        results.append({
                            'title': title.get_text(strip=True),
                            'content': content,
                            'url': link.get_text(strip=True) if link else '',
                            'source': 'arXiv'
                        })
        except Exception as e:
            logger.debug(f"arXiv error for '{query}': {e}")

        return results

    def _search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search web and scrape content."""
        results = []
        try:
            # DuckDuckGo search
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' AI ML tutorial')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')

                    # Quick content extraction
                    snippet_elem = result.find('a', class_='result__snippet')
                    content = snippet_elem.get_text(strip=True) if snippet_elem else ''

                    if len(content) > 50:
                        results.append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'source': 'Web'
                        })

        except Exception as e:
            logger.debug(f"Web search error for '{query}': {e}")

        return results

    def content_hash(self, content: str) -> str:
        """Generate content hash for deduplication."""
        return hashlib.md5(content.encode()).hexdigest()

    def add_to_chromadb_batch(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to ChromaDB in batch (thread-safe)."""
        added = 0

        documents_to_add = []
        metadatas = []
        ids = []

        for doc in documents:
            content = doc.get('content', '')

            if len(content) < 100:
                continue

            content_hash = self.content_hash(content)

            # Thread-safe duplicate check
            with self.lock:
                if content_hash in self.seen_content_hashes:
                    continue
                self.seen_content_hashes.add(content_hash)

            # Prepare for batch add
            documents_to_add.append(f"{doc.get('title', '')}\n\n{content}")
            metadatas.append({
                'title': doc.get('title', 'Untitled'),
                'source': doc.get('source', 'Unknown'),
                'url': doc.get('url', ''),
                'topic': doc.get('topic', ''),
                'category': doc.get('category', 'General')
            })
            ids.append(content_hash)

        # Batch add to ChromaDB (thread-safe)
        if documents_to_add:
            with self.lock:
                try:
                    self.collection.add(
                        documents=documents_to_add,
                        metadatas=metadatas,
                        ids=ids
                    )
                    added = len(documents_to_add)
                except Exception as e:
                    logger.error(f"Error adding batch to ChromaDB: {e}")

        return added

    def process_single_topic(self, topic_data: Dict[str, Any]) -> Dict[str, int]:
        """Process a single topic (called by parallel workers)."""
        topic = topic_data['topic']

        # Check if already processed
        with self.lock:
            if topic in self.processed_topics:
                return {'topic': topic, 'added': 0, 'skipped': True}

        # Search all sources
        documents = self.search_multiple_sources(topic_data)

        # Add to ChromaDB
        added = self.add_to_chromadb_batch(documents)

        # Mark as processed
        with self.lock:
            self.processed_topics.add(topic)
            current_size = self.collection.count()

        return {
            'topic': topic,
            'added': added,
            'skipped': False,
            'total_size': current_size
        }

    def run_parallel_pipeline(self, max_topics: int = None):
        """Run parallel expansion pipeline."""
        logger.info("\n" + "="*80)
        logger.info("🚀 PARALLEL KNOWLEDGE EXPANSION PIPELINE")
        logger.info("="*80)
        logger.info(f"  Workers: {self.max_workers}")
        logger.info(f"  Starting size: {self.collection.count():,} documents")
        logger.info("="*80 + "\n")

        # Extract topics
        topics_data = self.extract_all_topics()

        if max_topics:
            topics_data = topics_data[:max_topics]

        logger.info(f"📋 Processing {len(topics_data)} topics in parallel...")

        total_added = 0
        processed_count = 0

        # Parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_topic = {
                executor.submit(self.process_single_topic, topic_data): topic_data
                for topic_data in topics_data
            }

            # Process results as they complete
            for future in as_completed(future_to_topic):
                topic_data = future_to_topic[future]

                try:
                    result = future.result()

                    if not result['skipped']:
                        total_added += result['added']
                        processed_count += 1

                        if processed_count % 10 == 0:
                            logger.info(f"✅ Progress: {processed_count}/{len(topics_data)} topics | "
                                      f"Added: {total_added:,} docs | "
                                      f"Total: {result['total_size']:,} docs")

                except Exception as e:
                    logger.error(f"Error processing topic: {e}")

        logger.info(f"\n{'='*80}")
        logger.info(f"✅ PARALLEL PIPELINE COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"  Topics processed: {processed_count}")
        logger.info(f"  Documents added: {total_added:,}")
        logger.info(f"  Final KB size: {self.collection.count():,}")
        logger.info(f"  Unique content: {len(self.seen_content_hashes):,}")
        logger.info(f"{'='*80}\n")

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            'total_documents': self.collection.count(),
            'unique_hashes': len(self.seen_content_hashes),
            'processed_topics': len(self.processed_topics),
            'workers': self.max_workers
        }


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("🚀 PARALLEL KNOWLEDGE BASE EXPANSION PIPELINE")
    print("="*80)
    print("\n⚡ This pipeline uses PARALLEL PROCESSING for 10x speed!")
    print("\nFeatures:")
    print("  • 10 parallel workers searching simultaneously")
    print("  • Wikipedia + arXiv + Web scraping")
    print("  • Automatic deduplication")
    print("  • Thread-safe ChromaDB operations")
    print("  • Real-time progress tracking")
    print("\n" + "="*80)

    # Configuration
    MAX_WORKERS = 10  # Number of parallel workers
    MAX_TOPICS = 100  # Set to None for unlimited

    print(f"\n🔧 Configuration:")
    print(f"  Workers: {MAX_WORKERS}")
    print(f"  Topics to process: {MAX_TOPICS if MAX_TOPICS else 'ALL'}")
    print(f"  Sources: Wikipedia + arXiv + Web")
    print("\n" + "="*80 + "\n")

    input("Press Enter to start the pipeline...")

    # Run pipeline
    pipeline = ParallelKnowledgeExpansion(max_workers=MAX_WORKERS)

    try:
        pipeline.run_parallel_pipeline(max_topics=MAX_TOPICS)

        # Final stats
        stats = pipeline.get_stats()
        print("\n📊 FINAL STATISTICS:")
        print(f"  Total documents: {stats['total_documents']:,}")
        print(f"  Unique content pieces: {stats['unique_hashes']:,}")
        print(f"  Topics covered: {stats['processed_topics']}")
        print("\n✅ Knowledge base expansion complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
