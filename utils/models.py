from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SitemapImageEntry:
    relative_url: str
    title: Optional[str]
    caption: Optional[str]
