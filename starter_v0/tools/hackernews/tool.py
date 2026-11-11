from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

ENDPOINTS = {"relevance": "search", "date": "search_by_date"}


def search_hackernews(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        query = (query or "").strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must be a non-empty string")
        if sort not in ENDPOINTS:
            raise ValueError(f"sort must be one of {sorted(ENDPOINTS)}, got '{sort}'")
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5
        limit = max(1, min(limit, 20))
        response = requests.get(
            f"https://hn.algolia.com/api/v1/{ENDPOINTS[sort]}",
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = []
        for hit in response.json().get("hits", []):
            object_id = hit.get("objectID")
            if not object_id:
                continue
            items.append({
                "title": hit.get("title") or "",
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                "source": "news.ycombinator.com",
                "summary": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments, by {hit.get('author') or 'unknown'}",
                "date": hit.get("created_at"),
            })
        return {"tool": "search_hackernews", "query": query, "sort": sort, "items": items[:limit]}
    except Exception as exc:
        return err("search_hackernews", exc)
