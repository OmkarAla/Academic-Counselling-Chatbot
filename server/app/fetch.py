"""Fetch and extract the readable text from an admissions page.

trafilatura picks the wrong block on amrita.edu (the mega-menu), so this uses
a DOM strip: drop script/style/header/footer/nav/aside, then keep lines long
enough to be content rather than menu labels. Line-level duplication is
removed here; cross-page duplication is removed at ingest time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

MIN_LINE = 30


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str
    fetched_at: str


def fetch_page(url: str, timeout: float = 30.0) -> Page:
    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={"user-agent": "amrita-admissions-assistant/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url

    lines: list[str] = []
    seen: set[str] = set()
    for raw in soup.get_text("\n").splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if len(line) < MIN_LINE or line in seen:
            continue
        seen.add(line)
        lines.append(line)

    return Page(
        url=url,
        title=title,
        text="\n\n".join(lines),
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
