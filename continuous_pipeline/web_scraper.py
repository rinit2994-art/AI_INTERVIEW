"""
Web Scraper for Continuous Pipeline
Fetches content from multiple sources: GitHub issues, Medium, arXiv, tech blogs
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import feedparser
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """
    Multi-source web scraper for continuous content fetching
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.gemini_api_key = gemini_api_key or "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"

        # Track last fetch time for each source
        self.last_fetch = {}

        # Source configurations
        self.sources = {
            'hacker_news': {
                'url': 'https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=10',
                'enabled': True
            },
            'arxiv_ai': {
                'url': 'http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10',
                'enabled': True
            },
            'github_trending': {
                'url': 'https://api.github.com/search/repositories?q=stars:>1000+language:python&sort=updated&order=desc&per_page=5',
                'enabled': True
            },
            'medium_ai': {
                'url': 'https://medium.com/tag/artificial-intelligence/latest',
                'enabled': True
            }
        }

        logger.info(f"✅ WebScraper initialized with {len(self.sources)} sources")

    def fetch_hacker_news(self) -> List[Dict[str, Any]]:
        """Fetch latest stories from Hacker News"""
        try:
            response = self.session.get(
                self.sources['hacker_news']['url'],
                timeout=10
            )
            data = response.json()

            documents = []
            for hit in data.get('hits', [])[:5]:
                title = hit.get('title', '')
                url = hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}")
                text = hit.get('story_text', '')

                if not title:
                    continue

                content = f"Title: {title}\n\n"
                if text:
                    content += f"Content: {text}"
                else:
                    content += f"URL: {url}"

                documents.append({
                    'content': content,
                    'metadata': {
                        'url': url,
                        'title': title,
                        'source': 'hacker_news',
                        'type': 'article',
                        'fetched_at': datetime.utcnow().isoformat()
                    }
                })

            logger.info(f"📰 HackerNews: {len(documents)} articles")
            return documents

        except Exception as e:
            logger.error(f"❌ HackerNews error: {e}")
            return []

    def fetch_arxiv(self) -> List[Dict[str, Any]]:
        """Fetch latest AI papers from arXiv"""
        try:
            response = self.session.get(
                self.sources['arxiv_ai']['url'],
                timeout=10
            )

            feed = feedparser.parse(response.content)
            documents = []

            for entry in feed.entries[:5]:
                title = entry.get('title', '').replace('\n', ' ')
                summary = entry.get('summary', '').replace('\n', ' ')
                link = entry.get('link', '')

                content = f"Title: {title}\n\nAbstract: {summary}"

                documents.append({
                    'content': content,
                    'metadata': {
                        'url': link,
                        'title': title,
                        'source': 'arxiv',
                        'type': 'paper',
                        'fetched_at': datetime.utcnow().isoformat()
                    }
                })

            logger.info(f"📄 arXiv: {len(documents)} papers")
            return documents

        except Exception as e:
            logger.error(f"❌ arXiv error: {e}")
            return []

    def fetch_github_trending(self) -> List[Dict[str, Any]]:
        """Fetch trending GitHub repositories"""
        try:
            response = self.session.get(
                self.sources['github_trending']['url'],
                timeout=10
            )
            data = response.json()

            documents = []
            for repo in data.get('items', [])[:5]:
                name = repo.get('full_name', '')
                description = repo.get('description', '')
                url = repo.get('html_url', '')
                stars = repo.get('stargazers_count', 0)
                language = repo.get('language', 'Unknown')

                content = f"Repository: {name}\n"
                content += f"Language: {language} | Stars: {stars}\n\n"
                content += f"Description: {description}"

                # Fetch README if available
                try:
                    readme_url = f"https://api.github.com/repos/{name}/readme"
                    readme_resp = self.session.get(readme_url, timeout=5)
                    if readme_resp.status_code == 200:
                        readme_data = readme_resp.json()
                        readme_url_download = readme_data.get('download_url')
                        if readme_url_download:
                            readme_content = self.session.get(readme_url_download, timeout=5).text[:2000]
                            content += f"\n\nREADME excerpt:\n{readme_content}"
                except:
                    pass

                documents.append({
                    'content': content,
                    'metadata': {
                        'url': url,
                        'title': name,
                        'source': 'github',
                        'type': 'repository',
                        'stars': stars,
                        'language': language,
                        'fetched_at': datetime.utcnow().isoformat()
                    }
                })

            logger.info(f"⭐ GitHub: {len(documents)} repositories")
            return documents

        except Exception as e:
            logger.error(f"❌ GitHub error: {e}")
            return []

    def fetch_medium_rss(self) -> List[Dict[str, Any]]:
        """Fetch latest AI articles from Medium RSS"""
        try:
            # Medium RSS feeds
            rss_urls = [
                'https://medium.com/feed/tag/artificial-intelligence',
                'https://medium.com/feed/tag/machine-learning'
            ]

            documents = []
            for rss_url in rss_urls[:1]:  # Just first one for now
                try:
                    response = self.session.get(rss_url, timeout=10)
                    feed = feedparser.parse(response.content)

                    for entry in feed.entries[:3]:
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        link = entry.get('link', '')

                        # Clean HTML from summary
                        soup = BeautifulSoup(summary, 'html.parser')
                        clean_summary = soup.get_text()[:1000]

                        content = f"Title: {title}\n\nSummary: {clean_summary}"

                        documents.append({
                            'content': content,
                            'metadata': {
                                'url': link,
                                'title': title,
                                'source': 'medium',
                                'type': 'article',
                                'fetched_at': datetime.utcnow().isoformat()
                            }
                        })

                except Exception as e:
                    logger.error(f"Medium RSS error for {rss_url}: {e}")
                    continue

            logger.info(f"✍️  Medium: {len(documents)} articles")
            return documents

        except Exception as e:
            logger.error(f"❌ Medium error: {e}")
            return []

    def fetch_tech_blogs(self) -> List[Dict[str, Any]]:
        """Fetch from tech blogs via RSS"""
        try:
            rss_feeds = [
                'https://aws.amazon.com/blogs/machine-learning/feed/',
                'https://openai.com/blog/rss.xml',
                'https://blog.google/technology/ai/rss/'
            ]

            documents = []
            for feed_url in rss_feeds[:2]:  # Limit to 2 to avoid rate limits
                try:
                    response = self.session.get(feed_url, timeout=10)
                    feed = feedparser.parse(response.content)

                    for entry in feed.entries[:2]:
                        title = entry.get('title', '')
                        summary = entry.get('summary', entry.get('description', ''))
                        link = entry.get('link', '')

                        # Clean HTML
                        soup = BeautifulSoup(summary, 'html.parser')
                        clean_summary = soup.get_text()[:1000]

                        content = f"Title: {title}\n\nContent: {clean_summary}"

                        documents.append({
                            'content': content,
                            'metadata': {
                                'url': link,
                                'title': title,
                                'source': 'tech_blog',
                                'type': 'blog_post',
                                'fetched_at': datetime.utcnow().isoformat()
                            }
                        })

                except Exception as e:
                    logger.error(f"Blog RSS error for {feed_url}: {e}")
                    continue

            logger.info(f"📝 TechBlogs: {len(documents)} posts")
            return documents

        except Exception as e:
            logger.error(f"❌ TechBlogs error: {e}")
            return []

    def fetch_all(self) -> List[Dict[str, Any]]:
        """
        Fetch content from all enabled sources

        Returns:
            List of documents with content and metadata
        """
        logger.info("🌐 Fetching from all sources...")

        all_documents = []

        # Fetch from each source
        if self.sources['hacker_news']['enabled']:
            all_documents.extend(self.fetch_hacker_news())
            time.sleep(1)  # Rate limiting

        if self.sources['arxiv_ai']['enabled']:
            all_documents.extend(self.fetch_arxiv())
            time.sleep(1)

        if self.sources['github_trending']['enabled']:
            all_documents.extend(self.fetch_github_trending())
            time.sleep(1)

        if self.sources['medium_ai']['enabled']:
            all_documents.extend(self.fetch_medium_rss())
            time.sleep(1)

        # Tech blogs
        all_documents.extend(self.fetch_tech_blogs())

        logger.info(f"✅ Total fetched: {len(all_documents)} documents from all sources")

        return all_documents


if __name__ == "__main__":
    # Test scraper
    print("\n" + "="*80)
    print("🧪 Testing Web Scraper")
    print("="*80 + "\n")

    scraper = WebScraper()
    documents = scraper.fetch_all()

    print(f"\n✅ Fetched {len(documents)} documents")
    print("\nSample documents:\n")

    for i, doc in enumerate(documents[:3], 1):
        print(f"{i}. {doc['metadata']['source']} - {doc['metadata']['title']}")
        print(f"   URL: {doc['metadata']['url']}")
        print(f"   Content preview: {doc['content'][:150]}...")
        print()

    print("="*80)
