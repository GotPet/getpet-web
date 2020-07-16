from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SitemapImageEntry:
    relative_url: str
    title: Optional[str]
    caption: Optional[str]


@dataclass(frozen=True)
class PageInfoEntry:
    text: str
    url: Optional[str]
    is_active: bool


@dataclass(frozen=True)
class PaginationInfo:
    previous_url: Optional[str]
    next_url: Optional[str]
    entries: List[PageInfoEntry]
