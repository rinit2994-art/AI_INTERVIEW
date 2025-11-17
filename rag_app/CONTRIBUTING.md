# Contributing to AI Knowledge RAG System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check if the feature has been requested
2. Create an issue describing:
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   black backend config
   flake8 backend config
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide clear description
   - Link related issues
   - Wait for review

## 📝 Code Style Guidelines

### Python

- Follow PEP 8
- Use Black for formatting: `black backend config`
- Use type hints where appropriate
- Add docstrings to functions and classes
- Maximum line length: 100 characters

```python
def fetch_articles(source: str, max_count: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch articles from specified source.

    Args:
        source: The source to fetch from
        max_count: Maximum number of articles to fetch

    Returns:
        List of article dictionaries
    """
    pass
```

### Commit Messages

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add support for Reddit as article source
fix: Resolve ChromaDB connection timeout issue
docs: Update installation instructions
```

## 🧪 Testing

### Writing Tests

- Place tests in `tests/` directory
- Mirror the source structure
- Use pytest framework
- Aim for >80% code coverage

```python
# tests/test_article_fetcher.py
import pytest
from backend.services.article_fetcher import ArticleFetcher

@pytest.mark.asyncio
async def test_fetch_medium_articles():
    async with ArticleFetcher() as fetcher:
        articles = await fetcher.fetch_medium_articles(["ai"], max_per_tag=5)
        assert len(articles) <= 5
        assert all("title" in a for a in articles)
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_article_fetcher.py

# With coverage
pytest --cov=backend tests/

# Verbose output
pytest -v
```

## 🏗️ Project Structure

```
rag_app/
├── backend/           # Backend code
│   ├── agents/       # ADK agents
│   ├── api/          # FastAPI routes
│   └── services/     # Core services
├── config/           # Configuration
├── frontend/         # Frontend code
├── tests/            # Test files
└── docs/             # Documentation
```

## 🎯 Development Setup

1. **Clone and setup**
   ```bash
   git clone <repo-url>
   cd rag_app
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install dev dependencies**
   ```bash
   pip install pytest pytest-asyncio pytest-cov black flake8 mypy
   ```

3. **Setup pre-commit hooks** (optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run in development mode**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

## 📚 Areas for Contribution

### High Priority

- [ ] Add more data sources (Reddit, HackerNews, etc.)
- [ ] Implement caching layer (Redis)
- [ ] Add user authentication
- [ ] Improve error handling
- [ ] Add comprehensive tests

### Medium Priority

- [ ] Support for PDF/document upload
- [ ] Query history and bookmarks
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] GraphQL API

### Low Priority

- [ ] Mobile app
- [ ] Browser extension
- [ ] Slack/Discord integration
- [ ] Voice interface

## 🐛 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use FastAPI Debug Mode

```bash
uvicorn backend.api.main:app --reload --log-level debug
```

### Check ChromaDB Data

```python
import chromadb
client = chromadb.PersistentClient(path="./vector_db/chroma_data")
collection = client.get_collection("ai_knowledge_base")
print(collection.count())
```

## 📖 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add/update API documentation in FastAPI
- Update CHANGELOG.md for releases

## 🔄 Release Process

1. Update version in `backend/__init__.py`
2. Update CHANGELOG.md
3. Create release branch: `release/v1.x.x`
4. Tag the release: `git tag -a v1.x.x -m "Release v1.x.x"`
5. Push tag: `git push origin v1.x.x`
6. Create GitHub release with notes

## 💬 Communication

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and general discussion
- Pull Request comments: Code review and discussion

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

---

Thank you for contributing to AI Knowledge RAG System! 🚀
