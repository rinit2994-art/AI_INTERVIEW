"""Service for fetching articles from various sources."""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleFetcher:
    """Fetches articles from multiple sources."""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_medium_articles(self, tags: List[str], max_per_tag: int = 10) -> List[Dict[str, Any]]:
        """Fetch articles from Medium RSS feeds."""
        articles = []

        for tag in tags:
            try:
                # Medium RSS feed URL
                rss_url = f"https://medium.com/feed/tag/{tag}"
                logger.info(f"Fetching Medium articles for tag: {tag}")

                feed = feedparser.parse(rss_url)

                for entry in feed.entries[:max_per_tag]:
                    # Use summary/description as content
                    content = entry.get('summary', entry.get('description', ''))

                    if content:
                        articles.append({
                            "title": entry.title,
                            "content": content,
                            "url": entry.link,
                            "source": "Medium",
                            "category": tag,
                            "published_date": entry.get("published", ""),
                            "fetched_date": datetime.now().isoformat()
                        })
                        logger.info(f"Fetched: {entry.title}")

                # Be respectful with rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error fetching Medium tag {tag}: {e}")

        return articles

    async def fetch_arxiv_papers(self, categories: List[str], max_results: int = 20) -> List[Dict[str, Any]]:
        """Fetch papers from arXiv."""
        articles = []

        for category in categories:
            try:
                # arXiv API query
                base_url = "http://export.arxiv.org/api/query"
                query = f"cat:{category}"
                params = {
                    "search_query": query,
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                }

                logger.info(f"Fetching arXiv papers for category: {category}")

                async with self.session.get(base_url, params=params) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)

                        for entry in feed.entries:
                            articles.append({
                                "title": entry.title,
                                "content": entry.summary,
                                "url": entry.link,
                                "source": "arXiv",
                                "category": category,
                                "published_date": entry.published,
                                "fetched_date": datetime.now().isoformat()
                            })
                            logger.info(f"Fetched: {entry.title}")

                await asyncio.sleep(3)  # arXiv rate limiting

            except Exception as e:
                logger.error(f"Error fetching arXiv category {category}: {e}")

        return articles

    async def fetch_towards_data_science(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """Fetch articles from Towards Data Science."""
        articles = []

        try:
            rss_url = "https://towardsdatascience.com/feed"
            logger.info("Fetching Towards Data Science articles")

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:max_articles]:
                content = entry.get('summary', entry.get('description', ''))

                if content:
                    articles.append({
                        "title": entry.title,
                        "content": content,
                        "url": entry.link,
                        "source": "Towards Data Science",
                        "category": "data-science",
                        "published_date": entry.get("published", ""),
                        "fetched_date": datetime.now().isoformat()
                    })
                    logger.info(f"Fetched: {entry.title}")

        except Exception as e:
            logger.error(f"Error fetching Towards Data Science: {e}")

        return articles

    async def fetch_google_ai_blog(self, max_articles: int = 20) -> List[Dict[str, Any]]:
        """Fetch articles from Google AI Blog."""
        articles = []

        try:
            rss_url = "https://blog.research.google/feeds/posts/default"
            logger.info("Fetching Google AI Blog articles")

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:max_articles]:
                content = entry.get('summary', entry.get('description', ''))

                if content:
                    articles.append({
                        "title": entry.title,
                        "content": content,
                        "url": entry.link,
                        "source": "Google AI Blog",
                        "category": "ai-research",
                        "published_date": entry.get("published", ""),
                        "fetched_date": datetime.now().isoformat()
                    })
                    logger.info(f"Fetched: {entry.title}")

        except Exception as e:
            logger.error(f"Error fetching Google AI Blog: {e}")

        return articles

    async def fetch_all_sources(self) -> List[Dict[str, Any]]:
        """Fetch articles from all configured sources."""
        all_articles = []

        try:
            # Fetch from all sources concurrently
            tasks = [
                self.fetch_medium_articles(settings.medium_tags, max_per_tag=10),
                self.fetch_arxiv_papers(settings.arxiv_categories, max_results=20),
                self.fetch_towards_data_science(max_articles=20),
                self.fetch_google_ai_blog(max_articles=20)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in fetch task: {result}")

            logger.info(f"Total articles fetched: {len(all_articles)}")

        except Exception as e:
            logger.error(f"Error fetching all sources: {e}")

        return all_articles


async def main():
    """Test the article fetcher."""
    async with ArticleFetcher() as fetcher:
        articles = await fetcher.fetch_all_sources()
        print(f"Fetched {len(articles)} articles")
        for article in articles[:5]:
            print(f"- {article['title']} ({article['source']})")


if __name__ == "__main__":
    asyncio.run(main())
