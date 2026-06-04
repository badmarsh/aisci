"""
Citation Manager
================
Tracks URLs cited during research, deduplicates, and renders
APA / MLA / numbered bibliographies in the final report.

Usage:
    from src.citation_manager import CitationManager
    cm = CitationManager()
    cm.add(url="https://arxiv.org/abs/2301.00001", title="Paper Title",
           authors=["Author A", "Author B"], year=2023)
    inline = cm.cite("https://arxiv.org/abs/2301.00001")  # "[1]"
    report_with_refs = cm.inject_into_report(report_text)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Citation:
    url: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    accessed: str | None = None
    index: int = 0


class CitationManager:
    """Collect, deduplicate, and render citations for a research session."""

    def __init__(self) -> None:
        self._by_url: dict[str, Citation] = {}
        self._ordered: list[Citation] = []
        self._counter = 0

    def add(
        self,
        url: str,
        title: str,
        authors: list[str] | None = None,
        year: int | None = None,
        journal: str | None = None,
        accessed: str | None = None,
    ) -> Citation:
        """Register a source. Duplicate URLs are silently merged."""
        url = url.strip()
        if url not in self._by_url:
            self._by_url[url] = Citation(
                url=url, title=title, authors=authors or [],
                year=year, journal=journal, accessed=accessed,
            )
        return self._by_url[url]

    def add_from_search_result(self, result: dict) -> Citation:
        return self.add(
            url=result.get("url", ""),
            title=result.get("title", result.get("url", "")),
        )

    def cite(self, url: str) -> str:
        """Mark a URL as cited; return inline tag e.g. '[3]'."""
        url = url.strip()
        if url not in self._by_url:
            self.add(url=url, title=url)
        c = self._by_url[url]
        if c.index == 0:
            self._counter += 1
            c.index = self._counter
            self._ordered.append(c)
        return f"[{c.index}]"

    def render(self, style: Literal["apa", "mla", "numbered"] = "apa") -> str:
        """Return a Markdown bibliography for all cited sources."""
        if not self._ordered:
            return ""
        lines = ["## References\n"]
        for c in sorted(self._ordered, key=lambda x: x.index):
            lines.append(self._format(c, style))
        return "\n".join(lines)

    def _format(self, c: Citation, style: str) -> str:
        authors_str = ", ".join(c.authors) if c.authors else "Unknown"
        year_str    = f" ({c.year})" if c.year else ""
        title_str   = c.title or c.url
        journal_str = f" *{c.journal}*" if c.journal else ""
        accessed    = f" Retrieved {c.accessed}." if c.accessed else ""
        if style == "apa":
            return f"{c.index}. {authors_str}{year_str}. {title_str}.{journal_str} {c.url}{accessed}"
        elif style == "mla":
            return (
                f"{c.index}. {authors_str}. \"{title_str}.\""
                + (f" {c.journal}," if c.journal else "")
                + (f" {c.year}," if c.year else "")
                + f" {c.url}.{accessed}"
            )
        return f"[{c.index}] {title_str} -- {c.url}"

    def inject_into_report(self, report_text: str) -> str:
        bib = self.render()
        if not bib:
            return report_text
        return report_text.rstrip() + "\n\n" + bib

    def extract_urls_from_text(self, text: str) -> list[str]:
        urls = re.findall(r'https?://[^\s\)\]\>\"]+', text)
        for url in urls:
            if url not in self._by_url:
                self.add(url=url, title=url)
        return urls

    @property
    def count(self) -> int:
        return len(self._ordered)
