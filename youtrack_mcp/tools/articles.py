"""
YouTrack Articles (Knowledge Base) MCP tools.
"""

import logging
from typing import Any, Dict, Optional

from youtrack_mcp.api.client import YouTrackClient
from youtrack_mcp.api.articles import ArticlesClient
from youtrack_mcp.mcp_wrappers import sync_wrapper
from youtrack_mcp.utils import format_json_response

logger = logging.getLogger(__name__)


class ArticleTools:
    """Article (Knowledge Base) related MCP tools."""

    def __init__(self) -> None:
        """Initialize the article tools."""
        self.client = YouTrackClient()
        self.articles_api = ArticlesClient(self.client)

    def close(self) -> None:
        """Close the API client."""
        if hasattr(self.client, "close"):
            try:
                self.client.close()
            except Exception:  # pragma: no cover
                logger.exception("Failed to close YouTrackClient")

    @sync_wrapper
    def get_articles(
        self,
        project_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
        include_content: bool = False,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a list of articles, optionally filtered by project.
        FORMAT: get_articles(project_id="DEMO", limit=20, skip=0, include_content=False)
        Returns: JSON string with articles list
        """
        try:
            if project_id:
                articles = self.articles_api.list_project_articles(
                    project_id=project_id,
                    top=limit,
                    skip=skip,
                    include_content=include_content,
                    fields=fields,
                )
            else:
                articles = self.articles_api.list_articles(
                    top=limit,
                    skip=skip,
                    include_content=include_content,
                    fields=fields,
                )
            # Pydantic models -> dict for JSON
            result = [a.model_dump() if hasattr(a, "model_dump") else a for a in articles]
            return format_json_response(result)
        except Exception as e:  # pragma: no cover
            logger.exception("Error getting articles")
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def get_article(
        self,
        article_id: str,
        include_content: bool = True,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single article by ID.
        FORMAT: get_article(article_id="226-0", include_content=True)
        Returns: JSON string with article details
        """
        try:
            if not article_id:
                return format_json_response({"error": "Article ID is required"})
            article = self.articles_api.get_article(
                article_id=article_id,
                include_content=include_content,
                fields=fields,
            )
            result = article.model_dump() if hasattr(article, "model_dump") else article
            return format_json_response(result)
        except Exception as e:  # pragma: no cover
            logger.exception("Error getting article %s", article_id)
            return format_json_response({"error": str(e)})

    @sync_wrapper
    def get_article_children(
        self,
        article_id: str,
        limit: int = 20,
        skip: int = 0,
        include_content: bool = False,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get child (sub-)articles of a given article.
        FORMAT: get_article_children(article_id="226-0", limit=10, skip=0, include_content=False)
        Returns: JSON string with sub-articles
        """
        try:
            if not article_id:
                return format_json_response({"error": "Article ID is required"})
            children = self.articles_api.list_child_articles(
                article_id=article_id,
                top=limit,
                skip=skip,
                include_content=include_content,
                fields=fields,
            )
            result = [c.model_dump() if hasattr(c, "model_dump") else c for c in children]
            return format_json_response(result)
        except Exception as e:  # pragma: no cover
            logger.exception("Error getting child articles for %s", article_id)
            return format_json_response({"error": str(e)})

    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get tool definitions with descriptions (MCP discovery)."""
        return {
            "get_articles": {
                "description": (
                    "Get a list of knowledge base articles. "
                    "Optionally filter by project. "
                    'Example: get_articles(project_id="DEMO", limit=10)'
                ),
                "function": self.get_articles,
                "parameter_descriptions": {
                    "project_id": "Project identifier like 'DEMO' or '0-0' (optional)",
                    "limit": "Maximum number of articles to return (default: 20)",
                    "skip": "Number of articles to skip for pagination (default: 0)",
                    "include_content": "Include the article content body (default: False)",
                    "fields": "YouTrack 'fields' parameter to control returned attributes (optional)",
                },
            },
            "get_article": {
                "description": (
                    "Get a knowledge base article by ID. "
                    'Example: get_article(article_id="226-0")'
                ),
                "function": self.get_article,
                "parameter_descriptions": {
                    "article_id": "Article database ID like '226-0' (or idReadable if your API supports it)",
                    "include_content": "Include the full content body (default: True)",
                    "fields": "YouTrack 'fields' parameter to control returned attributes (optional)",
                },
            },
            "get_article_children": {
                "description": (
                    "Get sub-articles for a given article. "
                    'Example: get_article_children(article_id="226-0", limit=10)'
                ),
                "function": self.get_article_children,
                "parameter_descriptions": {
                    "article_id": "Parent article database ID like '226-0'",
                    "limit": "Maximum number of sub-articles to return (default: 20)",
                    "skip": "Number of items to skip for pagination (default: 0)",
                    "include_content": "Include the content body (default: False)",
                    "fields": "YouTrack 'fields' parameter to control returned attributes (optional)",
                },
            },
        }
