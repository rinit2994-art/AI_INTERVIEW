"""
Google ADK Documentation Scraper
Scrapes https://google.github.io/adk-docs/ and extracts all content
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from typing import List, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ADKDocsScraper:
    """Scrape Google ADK documentation."""

    def __init__(self, base_url: str = "https://google.github.io/adk-docs/"):
        self.base_url = base_url
        self.visited_urls: Set[str] = set()
        self.documents: List[Dict[str, str]] = []

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and within ADK docs domain."""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)

        # Must be same domain
        if parsed.netloc != base_parsed.netloc:
            return False

        # Skip anchors
        if '#' in url:
            url = url.split('#')[0]

        # Skip common non-content files
        skip_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.pdf']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        return True

    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract text content from a page."""
        try:
            logger.info(f"Scraping: {url}")

            # Add headers to avoid 403
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url

            # Get main content
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)

            # Clean up content
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)

            # Get all links for crawling
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if self.is_valid_url(full_url):
                    links.append(full_url)

            return {
                'url': url,
                'title': title_text,
                'content': content,
                'links': list(set(links))  # Remove duplicates
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def crawl(self, max_pages: int = 100, delay: float = 0.5):
        """Crawl the ADK documentation."""
        logger.info(f"Starting crawl of {self.base_url}")

        urls_to_visit = [self.base_url]

        while urls_to_visit and len(self.documents) < max_pages:
            url = urls_to_visit.pop(0)

            # Skip if already visited
            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)

            # Extract content
            doc = self.extract_content(url)

            if doc and len(doc['content']) > 100:  # Skip pages with little content
                self.documents.append({
                    'url': doc['url'],
                    'title': doc['title'],
                    'content': doc['content']
                })

                # Add new links to visit
                for link in doc['links']:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)

                logger.info(f"Scraped {len(self.documents)} pages so far...")

            # Be polite - add delay
            time.sleep(delay)

        logger.info(f"Crawling complete! Scraped {len(self.documents)} pages")
        return self.documents

    def save_to_json(self, filepath: str):
        """Save scraped documents to JSON."""
        logger.info(f"Saving to {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.documents)} documents")


def main():
    """Main scraping function."""
    print("="*80)
    print("🌐 Google ADK Documentation Scraper")
    print("="*80)

    scraper = ADKDocsScraper()

    print("\n📥 Starting to crawl https://google.github.io/adk-docs/...")
    print("This may take a few minutes...\n")

    documents = scraper.crawl(max_pages=50, delay=0.5)

    print(f"\n✅ Scraped {len(documents)} pages!")

    # Save to JSON
    output_file = '/home/user/AI_INTERVIEW/rag_app/adk_docs_content.json'
    scraper.save_to_json(output_file)

    print(f"\n💾 Saved to: {output_file}")

    # Show sample
    if documents:
        print(f"\n📄 Sample document:")
        print(f"   Title: {documents[0]['title']}")
        print(f"   URL: {documents[0]['url']}")
        print(f"   Content length: {len(documents[0]['content'])} characters")

    print("\n" + "="*80)
    print("✅ Scraping complete!")
    print("="*80)


if __name__ == "__main__":
    main()
