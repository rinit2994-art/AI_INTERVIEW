import asyncio
import logging
from backend.services.article_fetcher import ArticleFetcher
from backend.services.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the RAG pipeline."""
    logger.info("Starting RAG pipeline...")

    # Initialize vector store
    vector_store = get_vector_store()

    # Fetch articles
    async with ArticleFetcher() as fetcher:
        articles = await fetcher.fetch_all_sources()

    # Add articles to vector store
    if articles:
        num_added = vector_store.add_documents(articles)
        logger.info(f"Added {num_added} document chunks to knowledge base")
    else:
        logger.warning("No articles fetched")

    logger.info("RAG pipeline finished.")

if __name__ == "__main__":
    asyncio.run(main())
