"""
Knowledge Base Expansion Pipeline
Automatically searches the internet for all topics and builds a massive ChromaDB knowledge base
"""

import json
import time
import hashlib
import logging
from typing import List, Dict, Any, Set
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from knowledge_base_manager_v2 import KnowledgeBaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeExpansionPipeline:
    """Expand knowledge base by searching the internet for all topics."""

    def __init__(self, chroma_path: str = "./chroma_db"):
        self.kb_manager = KnowledgeBaseManager()
        self.seen_content_hashes: Set[str] = set()
        self.processed_topics: Set[str] = set()

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=False,
            persist_directory=chroma_path
        ))

        # Create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="mega_knowledge_base",
            metadata={"description": "Largest AI/ML/Tech Knowledge Base"}
        )

        logger.info(f"ChromaDB initialized. Current entries: {self.collection.count()}")

    def extract_all_topics(self) -> List[str]:
        """Extract all unique topics from existing knowledge base."""
        logger.info("Extracting topics from knowledge base...")

        self.kb_manager.parse_typescript_kb()
        self.kb_manager.build_indexes()

        topics = set()

        # Extract from titles
        for entry in self.kb_manager.entries:
            topics.add(entry['title'])

            # Extract from keywords
            for keyword in entry.get('keywords', []):
                if len(keyword) > 3:  # Skip very short keywords
                    topics.add(keyword)

        # Sort by popularity (from keyword index)
        topic_list = []
        for topic in topics:
            count = len(self.kb_manager.keyword_index.get(topic.lower(), []))
            topic_list.append((topic, count))

        topic_list.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"Extracted {len(topic_list)} unique topics")
        return [topic for topic, _ in topic_list]

    def search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search DuckDuckGo for a topic."""
        logger.info(f"Searching DuckDuckGo: {query}")

        results = []
        try:
            # DuckDuckGo HTML search
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract search results
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True)
                    })

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")

        return results

    def search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search Wikipedia for a topic."""
        logger.info(f"Searching Wikipedia: {query}")

        try:
            # Wikipedia API
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
                if page_id != '-1':  # Page exists
                    return {
                        'title': page_data.get('title', ''),
                        'content': page_data.get('extract', ''),
                        'url': f"https://en.wikipedia.org/wiki/{quote_plus(query)}",
                        'source': 'Wikipedia'
                    }

        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")

        return None

    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search arXiv for research papers."""
        logger.info(f"Searching arXiv: {query}")

        results = []
        try:
            # arXiv API
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }

            response = requests.get(url, params=params, timeout=15)
            soup = BeautifulSoup(response.text, 'xml')

            for entry in soup.find_all('entry'):
                title = entry.find('title')
                summary = entry.find('summary')
                link = entry.find('id')

                if title and summary:
                    results.append({
                        'title': title.get_text(strip=True),
                        'content': summary.get_text(strip=True),
                        'url': link.get_text(strip=True) if link else '',
                        'source': 'arXiv'
                    })

        except Exception as e:
            logger.error(f"arXiv search error: {e}")

        return results

    def scrape_url_content(self, url: str) -> str:
        """Scrape content from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')

            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                # Clean up
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                return '\n'.join(lines)

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

        return ""

    def content_hash(self, content: str) -> str:
        """Generate hash for content deduplication."""
        return hashlib.md5(content.encode()).hexdigest()

    def add_to_chromadb(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to ChromaDB with deduplication."""
        added = 0

        for doc in documents:
            content = doc.get('content', '')

            # Skip if too short
            if len(content) < 100:
                continue

            # Check for duplicates
            content_hash = self.content_hash(content)
            if content_hash in self.seen_content_hashes:
                continue

            self.seen_content_hashes.add(content_hash)

            # Add to ChromaDB
            try:
                self.collection.add(
                    documents=[f"{doc.get('title', '')}\n\n{content}"],
                    metadatas=[{
                        'title': doc.get('title', 'Untitled'),
                        'source': doc.get('source', 'Web'),
                        'url': doc.get('url', ''),
                        'topic': doc.get('topic', ''),
                    }],
                    ids=[content_hash]
                )
                added += 1
            except Exception as e:
                logger.error(f"Error adding to ChromaDB: {e}")

        return added

    def expand_topic(self, topic: str) -> int:
        """Expand knowledge base for a single topic."""
        if topic in self.processed_topics:
            logger.info(f"Skipping already processed topic: {topic}")
            return 0

        logger.info(f"\n{'='*80}")
        logger.info(f"EXPANDING TOPIC: {topic}")
        logger.info(f"{'='*80}")

        all_documents = []

        # 1. Search Wikipedia
        wiki_result = self.search_wikipedia(topic)
        if wiki_result:
            wiki_result['topic'] = topic
            all_documents.append(wiki_result)
            logger.info(f"  ✓ Found Wikipedia article")

        # 2. Search arXiv
        arxiv_results = self.search_arxiv(topic)
        for result in arxiv_results:
            result['topic'] = topic
            all_documents.append(result)
        logger.info(f"  ✓ Found {len(arxiv_results)} arXiv papers")

        # 3. Search DuckDuckGo
        ddg_results = self.search_duckduckgo(topic)
        logger.info(f"  ✓ Found {len(ddg_results)} web results")

        # Scrape top results
        for i, result in enumerate(ddg_results[:5]):  # Limit to top 5
            url = result['url']
            if url and not url.startswith('javascript'):
                content = self.scrape_url_content(url)
                if content:
                    all_documents.append({
                        'title': result['title'],
                        'content': content,
                        'url': url,
                        'source': 'Web',
                        'topic': topic
                    })
                    logger.info(f"  ✓ Scraped: {result['title'][:50]}...")

                # Be polite
                time.sleep(1)

        # Add all to ChromaDB
        added = self.add_to_chromadb(all_documents)
        self.processed_topics.add(topic)

        logger.info(f"  ✅ Added {added} new documents for '{topic}'")
        logger.info(f"  📊 Total KB size: {self.collection.count():,} documents")

        return added

    def run_pipeline(self, max_topics: int = None, delay: float = 2.0):
        """Run the complete expansion pipeline."""
        logger.info("\n" + "="*80)
        logger.info("🚀 KNOWLEDGE BASE EXPANSION PIPELINE")
        logger.info("="*80 + "\n")

        # Extract topics
        topics = self.extract_all_topics()

        if max_topics:
            topics = topics[:max_topics]

        logger.info(f"📋 Processing {len(topics)} topics")
        logger.info(f"🔄 Current ChromaDB size: {self.collection.count():,} documents\n")

        total_added = 0

        for i, topic in enumerate(topics, 1):
            logger.info(f"\n[{i}/{len(topics)}] Processing: {topic}")

            added = self.expand_topic(topic)
            total_added += added

            # Progress update
            if i % 10 == 0:
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 PROGRESS UPDATE")
                logger.info(f"  Topics processed: {i}/{len(topics)}")
                logger.info(f"  Documents added: {total_added:,}")
                logger.info(f"  Total KB size: {self.collection.count():,}")
                logger.info(f"{'='*80}\n")

            # Be polite to servers
            time.sleep(delay)

        logger.info(f"\n{'='*80}")
        logger.info(f"✅ PIPELINE COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"  Topics processed: {len(topics)}")
        logger.info(f"  Documents added: {total_added:,}")
        logger.info(f"  Final KB size: {self.collection.count():,}")
        logger.info(f"  Unique content hashes: {len(self.seen_content_hashes):,}")
        logger.info(f"{'='*80}\n")

    def save_progress(self, filepath: str = "expansion_progress.json"):
        """Save progress to resume later."""
        progress = {
            'processed_topics': list(self.processed_topics),
            'total_documents': self.collection.count(),
            'unique_hashes': len(self.seen_content_hashes)
        }

        with open(filepath, 'w') as f:
            json.dump(progress, f, indent=2)

        logger.info(f"Progress saved to {filepath}")

    def load_progress(self, filepath: str = "expansion_progress.json"):
        """Load previous progress."""
        try:
            with open(filepath, 'r') as f:
                progress = json.load(f)

            self.processed_topics = set(progress.get('processed_topics', []))
            logger.info(f"Loaded progress: {len(self.processed_topics)} topics already processed")
        except FileNotFoundError:
            logger.info("No previous progress found, starting fresh")


def main():
    """Main execution function."""
    print("="*80)
    print("🚀 KNOWLEDGE BASE EXPANSION PIPELINE")
    print("="*80)
    print("\nThis will:")
    print("  1. Extract all topics from your 4,194 knowledge entries")
    print("  2. Search Wikipedia, arXiv, and the web for each topic")
    print("  3. Scrape and extract relevant content")
    print("  4. Store everything in ChromaDB with deduplication")
    print("  5. Create the LARGEST knowledge base ever!")
    print("\n" + "="*80)

    # Initialize pipeline
    pipeline = KnowledgeExpansionPipeline()

    # Load previous progress if any
    pipeline.load_progress()

    # Run pipeline
    # Start with top 50 topics for testing, remove limit for full run
    print("\n🔧 Configuration:")
    print("  Max topics: 50 (remove limit for full run)")
    print("  Delay between requests: 2 seconds")
    print("  Sources: Wikipedia + arXiv + Web scraping")
    print("\n" + "="*80 + "\n")

    try:
        pipeline.run_pipeline(max_topics=50, delay=2.0)

        # Save progress
        pipeline.save_progress()

        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Final knowledge base size: {pipeline.collection.count():,} documents")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        pipeline.save_progress()
        print("Progress saved. Run again to resume.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        pipeline.save_progress()
        print("Progress saved.")


if __name__ == "__main__":
    main()
