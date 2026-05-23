from __future__ import annotations

import httpx
from pydantic import BaseModel

from app.config import settings


class SearchResult(BaseModel):
    url: str
    title: str
    content: str
    provider: str = "tavily"


class TavilySearchProvider:
    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        if not self.api_key:
            raise RuntimeError("APP_TAVILY_API_KEY is required for Tavily search")

        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=30.0,
            trust_env=False,
        )
        response.raise_for_status()
        payload = response.json()

        return [
            SearchResult(
                url=item["url"],
                title=item.get("title", ""),
                content=item.get("content", ""),
                provider="tavily",
            )
            for item in payload.get("results", [])
        ]


def build_search_provider() -> TavilySearchProvider:
    if settings.search_provider != "tavily":
        raise ValueError(f"Unsupported search provider: {settings.search_provider}")
    return TavilySearchProvider(settings.tavily_api_key)
