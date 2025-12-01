"""
models.py
Core data structures.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class IndexedFile:
    path: str
    name: str
    extension: str
    size_bytes: int
    modified_time: float
    content: str
    preview: str = ""

    def as_dict(self):
        return {
            "path": self.path,
            "name": self.name,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "modified_time": self.modified_time,
            "content": self.content,
            "preview": self.preview
        }

@dataclass
class SearchResult:
    file: IndexedFile
    score: float
