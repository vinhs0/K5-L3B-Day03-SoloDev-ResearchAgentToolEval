from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

SUPPORTED_LANGS = {"en", "vi", "fr", "de", "es", "ja", "zh"}


def wikipedia_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    try:
        title = (title or "").strip() if isinstance(title, str) else ""
        if not title:
            raise ValueError("title must be a non-empty string")
        lang = (lang or "en").strip().lower() if isinstance(lang, str) else "en"
        if lang not in SUPPORTED_LANGS:
            raise ValueError(f"unsupported lang '{lang}', use one of {sorted(SUPPORTED_LANGS)}")
        response = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}",
            headers={"User-Agent": "research-agent-lab/1.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page", "")
        return {"tool": "wikipedia_summary", "title": title, "lang": lang, "items": [{
            "title": data.get("title") or title,
            "url": url,
            "source": f"{lang}.wikipedia.org",
            "summary": (data.get("extract") or "")[:2000],
        }]}
    except Exception as exc:
        return err("wikipedia_summary", exc)
