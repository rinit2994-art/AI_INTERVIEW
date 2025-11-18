"""
Continuous Pipeline - Fetch web content and store in ChromaDB
"""

__version__ = "1.0.0"
__author__ = "AI Interview Project"

from .chromadb_manager import ChromaDBManager
from .web_scraper import WebScraper
from .continuous_pipeline import ContinuousPipeline

__all__ = ['ChromaDBManager', 'WebScraper', 'ContinuousPipeline']
