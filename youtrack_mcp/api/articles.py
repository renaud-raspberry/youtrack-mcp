""" YouTrack Articles (Knowledge Base) API client.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from youtrack_mcp.api.client import YouTrackClient
import logging

logger = logging.getLogger(__name__)


class Article(BaseModel):
    """Model for a YouTrack knowledge base article."""
    # Allow extra fields returned by the API (tags, visibility, etc.)
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }

    id: str
    idReadable: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    project: Optional[Dict[str, Any]] = None
    reporter: Optional[Dict[str, Any]] = None
    updatedBy: Optional[Dict[str, Any]] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    hasChildren: Optional[bool] = None
    hasStar: Optional[bool] = None


class ArticlesClient:
    """Client for interacting with YouTrack Articles (Knowledge Base) API."""

    def __init__(self, client: YouTrackClient):
        """Initialize the Articles API client.
        Args:
            client: The YouTrack API client
        """
        self.client = client

    def _default_fields(self, include_content: bool = False) -> str:
        base = (
            "id,idReadable,summary,project(id,shortName),"
            "reporter(id,login,name),updated,created,hasChildren,hasStar"
        )
        return base + (",content" if include_content else "")

    def list_articles(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        include_content: bool = False,
        fields: Optional[str] = None,
    ) -> List[Article]:
        """Get a list of articles.
        See: GET /api/articles
        """
        params: Dict[str, Any] = {
            "fields": fields or self._default_fields(include_content),
        }
        if top is not None:
            params["$top"] = top
        if skip is not None:
            params["$skip"] = skip
        resp = self.client.get("articles", params=params)
        # API returns a list of dicts
        return [Article.model_validate(a) for a in resp]

    def get_article(
        self,
        article_id: str,
        include_content: bool = True,
        fields: Optional[str] = None,
    ) -> Article:
        """Get a specific article by ID.
        See: GET /api/articles/{articleID}
        """
        params = {"fields": fields or self._default_fields(include_content)}
        resp = self.client.get(f"articles/{article_id}", params=params)
        return Article.model_validate(resp)

    def list_child_articles(
        self,
        article_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        include_content: bool = False,
        fields: Optional[str] = None,
    ) -> List[Article]:
        """Get sub-articles of a given article.
        See: GET /api/articles/{articleID}/childArticles
        """
        params: Dict[str, Any] = {
            "fields": fields or self._default_fields(include_content),
        }
        if top is not None:
            params["$top"] = top
        if skip is not None:
            params["$skip"] = skip
        resp = self.client.get(f"articles/{article_id}/childArticles", params=params)
        return [Article.model_validate(a) for a in resp]

    def list_project_articles(
        self,
        project_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        include_content: bool = False,
        fields: Optional[str] = None,
    ) -> List[Article]:
        """Get articles for a specific project.
        See: GET /api/admin/projects/{projectID}/articles
        """
        params: Dict[str, Any] = {
            "fields": fields or self._default_fields(include_content),
        }
        if top is not None:
            params["$top"] = top
        if skip is not None:
            params["$skip"] = skip
        resp = self.client.get(f"admin/projects/{project_id}/articles", params=params)
        return [Article.model_validate(a) for a in resp]
