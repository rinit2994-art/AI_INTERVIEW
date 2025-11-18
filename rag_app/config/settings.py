"""Application configuration settings."""
import os
from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration (Hardcoded)
    gemini_api_key: str = "AIzaSyDDwq8X1v4rU9qoGTqeWGwVOaJDQvrZHYU"

    # Application
    app_name: str = "AI Knowledge RAG System"
    app_version: str = "1.0.0"
    debug: bool = True

    # Vector Database
    chroma_persist_directory: str = "./vector_db/chroma_data"
    collection_name: str = "ai_knowledge_base"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Gemini Model
    gemini_model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 2048

    # Scraping
    max_articles_per_source: int = 50
    fetch_interval_hours: int = 24

    # Sources
    medium_tags: List[str]
    arxiv_categories: List[str]

    @validator('medium_tags', 'arxiv_categories', pre=True)
    def _split_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',')]
        return v

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
