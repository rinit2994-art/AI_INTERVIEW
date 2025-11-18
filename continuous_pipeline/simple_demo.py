"""
SIMPLE DEMO - Continuous Pipeline
Demonstrates the concept without all dependencies
"""

import time
import json
import requests
from datetime import datetime
import hashlib
from typing import List, Dict

print("\n" + "="*80)
print("🚀 CONTINUOUS PIPELINE DEMO")
print("="*80)
print("\nThis demo shows the continuous pipeline concept:")
print("  1. Fetch content from web (HackerNews API)")
print("  2. Store with deduplication")
print("  3. Run every 10 seconds")
print("\nNote: Full version uses ChromaDB with all-mpnet-base-v2 embeddings")
print("="*80 + "\n")


class SimplePipeline:
    """Simple demonstration of continuous pipeline"""

    def __init__(self):
        self.documents = {}  # Simple in-memory storage
        self.iteration = 0

    def fetch_hackernews(self) -> List[Dict]:
        """Fetch from HackerNews API (with fallback simulation)"""
        try:
            url = "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=10"
            response = requests.get(url, timeout=10)
            data = response.json()

            docs = []
            for hit in data.get('hits', [])[:5]:
                title = hit.get('title', '')
                url = hit.get('url', '')
                text = hit.get('story_text', '')

                if not title:
                    continue

                doc_id = hashlib.md5(f"{url}:{title}".encode()).hexdigest()

                docs.append({
                    'id': doc_id,
                    'title': title,
                    'url': url,
                    'content': text or 'No text content',
                    'source': 'hackernews',
                    'fetched_at': datetime.utcnow().isoformat()
                })

            return docs

        except Exception as e:
            print(f"⚠️  Network restricted, using simulated data for demo")
            # Simulate data to demonstrate the concept
            import random
            topics = [
                "New Advances in AI Transformers",
                "ChromaDB Vector Database Released",
                "Understanding RAG Systems",
                "LangChain 2.0 Features",
                "Gemini API Updates",
                "PyTorch 3.0 Performance",
                "Kubernetes Best Practices",
                "FastAPI Production Tips"
            ]

            docs = []
            for i in range(random.randint(2, 5)):
                title = random.choice(topics)
                doc_id = hashlib.md5(f"{title}:{datetime.utcnow().isoformat()}".encode()).hexdigest()

                docs.append({
                    'id': doc_id,
                    'title': title,
                    'url': f'https://example.com/article/{doc_id[:8]}',
                    'content': f'Simulated content about {title}',
                    'source': 'simulated',
                    'fetched_at': datetime.utcnow().isoformat()
                })

            return docs

    def add_documents(self, docs: List[Dict]) -> int:
        """Add documents with deduplication"""
        added = 0
        for doc in docs:
            doc_id = doc['id']
            if doc_id not in self.documents:
                self.documents[doc_id] = doc
                added += 1
        return added

    def run_iteration(self):
        """Run one iteration"""
        self.iteration += 1

        print(f"\n{'─'*80}")
        print(f"🔄 Iteration {self.iteration} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─'*80}")

        # Fetch
        print("📥 Fetching from HackerNews...")
        docs = self.fetch_hackernews()
        print(f"   Fetched: {len(docs)} articles")

        # Store
        added = self.add_documents(docs)
        print(f"   Added: {added} new documents")
        print(f"   Total in storage: {len(self.documents)}")

        # Show samples
        if added > 0:
            print(f"\n📰 New articles:")
            for doc in docs[:min(2, added)]:
                if doc['id'] not in [d['id'] for d in list(self.documents.values())[:-added]]:
                    print(f"   • {doc['title'][:70]}")
                    print(f"     {doc['url'][:70]}")

    def run_continuous(self, interval=10, max_iterations=None):
        """Run continuously"""
        print(f"⏰ Running every {interval} seconds")
        print("   Press Ctrl+C to stop\n")

        iteration_count = 0
        try:
            while True:
                self.run_iteration()

                iteration_count += 1
                if max_iterations and iteration_count >= max_iterations:
                    break

                print(f"\n💤 Waiting {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")

        finally:
            print(f"\n{'='*80}")
            print("📊 FINAL STATS")
            print(f"{'='*80}")
            print(f"Total iterations: {self.iteration}")
            print(f"Total documents: {len(self.documents)}")
            print(f"{'='*80}\n")


def main():
    """Run demo"""
    import sys

    pipeline = SimplePipeline()

    # Check arguments
    if '--once' in sys.argv:
        print("Running single iteration...\n")
        pipeline.run_iteration()

    elif '--demo' in sys.argv:
        print("Running 3 iterations demo...\n")
        pipeline.run_continuous(interval=10, max_iterations=3)

    else:
        print("Running continuous mode...\n")
        pipeline.run_continuous(interval=10)


if __name__ == "__main__":
    main()
