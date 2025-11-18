"""
Knowledge Base Manager - Parse, Search, and Grow your 4,330+ entry knowledge base!
"""
import json
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manage and utilize the massive TypeScript knowledge base."""

    def __init__(self, ts_file_path: str = "/home/user/AI_INTERVIEW/knowledge_base.ts"):
        self.ts_file_path = ts_file_path
        self.entries: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[Dict]] = defaultdict(list)
        self.keyword_index: Dict[str, List[Dict]] = defaultdict(list)

    def parse_typescript_kb(self) -> List[Dict[str, Any]]:
        """Parse the TypeScript knowledge base file."""
        logger.info(f"Parsing knowledge base from {self.ts_file_path}")

        entries = []
        current_entry = {}
        in_content = False
        content_lines = []
        in_keywords = False

        with open(self.ts_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Start of new entry
            if line == '{' and i > 0 and 'knowledgeBase' not in lines[i-1]:
                current_entry = {}
                in_content = False
                content_lines = []
                in_keywords = False

            # Title
            elif line.startswith("title:"):
                match = re.search(r"title:\s*'([^']*)'", line)
                if not match:
                    match = re.search(r'title:\s*"([^"]*)"', line)
                if match:
                    current_entry['title'] = match.group(1)

            # Content start
            elif line.startswith("content:"):
                in_content = True
                # Extract inline content if present
                match = re.search(r"content:\s*'([^']*)'", line)
                if not match:
                    match = re.search(r'content:\s*"([^"]*)"', line)
                if match:
                    content_lines.append(match.group(1))
                    in_content = False
                else:
                    # Multi-line content starts
                    content_start = line.find("'")
                    if content_start == -1:
                        content_start = line.find('"')
                    if content_start != -1:
                        content_lines.append(line[content_start+1:])

            # Content continuation
            elif in_content and not line.startswith('keywords'):
                # Check if content ends
                if line.endswith("',") or line.endswith('",'):
                    content_lines.append(line[:-2])
                    current_entry['content'] = ' '.join(content_lines).replace('\\\'', "'")
                    in_content = False
                    content_lines = []
                else:
                    content_lines.append(line)

            # Keywords
            elif 'keywords:' in line:
                in_keywords = True
                # Try to extract keywords from single line
                match = re.search(r'keywords:\s*\[(.*?)\]', line)
                if match:
                    keywords_str = match.group(1)
                    keywords = [k.strip().strip("'\"") for k in keywords_str.split(',')]
                    current_entry['keywords'] = keywords
                    in_keywords = False
                else:
                    current_entry['keywords'] = []

            # Keywords continuation
            elif in_keywords:
                if ']' in line:
                    # Extract last keywords
                    keywords_part = line[:line.find(']')]
                    if keywords_part.strip():
                        for kw in keywords_part.split(','):
                            kw = kw.strip().strip("'\"")
                            if kw:
                                current_entry['keywords'].append(kw)
                    in_keywords = False
                else:
                    # Continue collecting keywords
                    for kw in line.split(','):
                        kw = kw.strip().strip("'\"")
                        if kw and kw != '[':
                            current_entry['keywords'].append(kw)

            # End of entry
            elif line in ['},', '}'] and current_entry.get('title'):
                # Save entry
                if 'content' in current_entry and 'keywords' in current_entry:
                    entries.append(current_entry.copy())
                current_entry = {}

            i += 1

        logger.info(f"Parsed {len(entries)} knowledge entries")
        self.entries = entries
        return entries

    def build_indexes(self):
        """Build category and keyword indexes for fast search."""
        logger.info("Building search indexes...")

        # Categorize entries (you can add category detection logic)
        for entry in self.entries:
            # Infer category from keywords or title
            keywords = entry.get('keywords', [])
            title = entry.get('title', '')

            # Simple categorization
            if any(k in ['statistics', 'probability'] for k in keywords):
                category = 'Statistics & Math'
            elif any(k in ['machine learning', 'ml', 'model'] for k in keywords):
                category = 'Machine Learning'
            elif any(k in ['deep learning', 'neural network', 'cnn', 'rnn'] for k in keywords):
                category = 'Deep Learning'
            elif any(k in ['nlp', 'natural language', 'text'] for k in keywords):
                category = 'NLP'
            elif any(k in ['computer vision', 'image', 'cnn'] for k in keywords):
                category = 'Computer Vision'
            elif any(k in ['data', 'dataset', 'preprocessing'] for k in keywords):
                category = 'Data Engineering'
            elif any(k in ['genai', 'generative', 'llm', 'transformer'] for k in keywords):
                category = 'Generative AI'
            else:
                category = 'General'

            entry['category'] = category
            self.categories[category].append(entry)

            # Build keyword index
            for keyword in keywords:
                self.keyword_index[keyword.lower()].append(entry)

        logger.info(f"Created {len(self.categories)} categories")
        logger.info(f"Indexed {len(self.keyword_index)} unique keywords")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Smart search across all entries."""
        query_lower = query.lower()
        scored_entries = []

        for entry in self.entries:
            score = 0
            title = entry.get('title', '').lower()
            content = entry.get('content', '').lower()
            keywords = [k.lower() for k in entry.get('keywords', [])]

            # Exact title match
            if query_lower == title:
                score += 1000

            # Title contains query
            elif query_lower in title:
                score += 500

            # Keyword match
            for keyword in keywords:
                if query_lower == keyword:
                    score += 200
                elif query_lower in keyword or keyword in query_lower:
                    score += 100

            # Content match
            if query_lower in content:
                score += content.count(query_lower) * 10

            # Word-by-word matching
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:
                    if word in title:
                        score += 50
                    if word in keywords:
                        score += 30
                    score += content.count(word) * 5

            if score > 0:
                scored_entries.append((score, entry))

        # Sort and return top_k
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        return [entry for score, entry in scored_entries[:top_k]]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        total_entries = len(self.entries)
        total_keywords = len(self.keyword_index)
        categories = len(self.categories)

        category_breakdown = {
            cat: len(entries) for cat, entries in self.categories.items()
        }

        top_keywords = sorted(
            self.keyword_index.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:20]

        avg_keywords_per_entry = sum(len(e.get('keywords', [])) for e in self.entries) / total_entries if total_entries > 0 else 0

        return {
            'total_entries': total_entries,
            'total_unique_keywords': total_keywords,
            'total_categories': categories,
            'category_breakdown': category_breakdown,
            'top_keywords': [(kw, len(entries)) for kw, entries in top_keywords],
            'avg_keywords_per_entry': round(avg_keywords_per_entry, 2)
        }

    def export_to_json(self, output_path: str):
        """Export knowledge base to JSON."""
        logger.info(f"Exporting to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported {len(self.entries)} entries")

    def export_to_python(self, output_path: str):
        """Export knowledge base as Python list."""
        logger.info(f"Exporting to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated from knowledge_base.ts\n")
            f.write("# Total entries: {}\n\n".format(len(self.entries)))
            f.write("knowledge_base = [\n")
            for entry in self.entries:
                f.write("    {\n")
                f.write(f"        'title': {repr(entry.get('title', ''))},\n")
                f.write(f"        'content': {repr(entry.get('content', ''))},\n")
                f.write(f"        'keywords': {repr(entry.get('keywords', []))},\n")
                f.write(f"        'category': {repr(entry.get('category', 'General'))},\n")
                f.write("    },\n")
            f.write("]\n")
        logger.info(f"Exported {len(self.entries)} entries as Python")

    def find_gaps(self, topic: str) -> Dict[str, Any]:
        """Find gaps in coverage for a topic."""
        results = self.search(topic, top_k=1000)

        return {
            'topic': topic,
            'entries_found': len(results),
            'coverage': 'High' if len(results) > 10 else 'Medium' if len(results) > 3 else 'Low',
            'sample_entries': [e['title'] for e in results[:5]]
        }

    def add_entry(self, title: str, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Add a new entry to the knowledge base."""
        new_entry = {
            'title': title,
            'content': content,
            'keywords': keywords
        }

        self.entries.append(new_entry)
        logger.info(f"Added new entry: {title}")

        return new_entry

    def suggest_related_topics(self, topic: str, limit: int = 10) -> List[str]:
        """Suggest related topics based on shared keywords."""
        results = self.search(topic, top_k=5)

        if not results:
            return []

        # Collect all keywords from matching entries
        related_keywords = set()
        for entry in results:
            related_keywords.update(entry.get('keywords', []))

        # Find entries with those keywords
        related_entries = []
        for keyword in related_keywords:
            entries = self.keyword_index.get(keyword.lower(), [])
            related_entries.extend(entries)

        # Get unique titles
        unique_titles = list(set(e['title'] for e in related_entries))

        # Remove original matches
        original_titles = set(e['title'] for e in results)
        unique_titles = [t for t in unique_titles if t not in original_titles]

        return unique_titles[:limit]


def main():
    """Demo the knowledge base manager."""
    print("="*80)
    print("🧠 KNOWLEDGE BASE MANAGER - 4,330+ Entries")
    print("="*80)

    # Initialize
    kb = KnowledgeBaseManager()

    # Parse
    print("\n📖 Parsing TypeScript knowledge base...")
    kb.parse_typescript_kb()

    # Build indexes
    print("\n🔍 Building search indexes...")
    kb.build_indexes()

    # Get stats
    print("\n📊 Knowledge Base Statistics:")
    stats = kb.get_stats()
    print(f"   Total Entries: {stats['total_entries']}")
    print(f"   Unique Keywords: {stats['total_unique_keywords']}")
    print(f"   Categories: {stats['total_categories']}")
    print(f"   Avg Keywords/Entry: {stats['avg_keywords_per_entry']}")

    print("\n📂 Category Breakdown:")
    for cat, count in stats['category_breakdown'].items():
        print(f"   {cat}: {count} entries")

    print("\n🔥 Top Keywords:")
    for keyword, count in stats['top_keywords'][:10]:
        print(f"   {keyword}: {count} entries")

    # Test search
    print("\n🔍 Testing Search...")
    test_queries = ['machine learning', 'neural network', 'gradient descent', 'statistics']
    for query in test_queries:
        results = kb.search(query, top_k=3)
        print(f"\n   Query: '{query}' - Found {len(results)} results")
        for r in results[:2]:
            print(f"      • {r['title']}")

    # Export
    print("\n💾 Exporting...")
    kb.export_to_json('/home/user/AI_INTERVIEW/rag_app/knowledge_base.json')
    kb.export_to_python('/home/user/AI_INTERVIEW/rag_app/knowledge_base.py')
    print("   ✓ Exported to JSON")
    print("   ✓ Exported to Python")

    print("\n✅ Done! Your knowledge base is ready to use!")
    print("="*80)


if __name__ == "__main__":
    main()
