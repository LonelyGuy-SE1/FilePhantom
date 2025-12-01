"""
indexer.py
Handles recursive file scanning and indexing.
"""

import os
import json
import time
from typing import List, Optional, Callable
from models import IndexedFile
import config

class FileIndexer:
    def __init__(self):
        self.root_path = ""
        self._index = []

    def set_root_path(self, path: str) -> None:
        self.root_path = path

    def index_files(self, progress_callback: Optional[Callable[[str], None]] = None) -> List[IndexedFile]:
        if not self.root_path or not os.path.isdir(self.root_path):
            return []

        indexed_files = []
        count = 0
        
        for root, _, files in os.walk(self.root_path):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in config.ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, filename)
                    
                    if progress_callback and count % 10 == 0:
                         progress_callback(f"Indexing... ({count} files)")

                    try:
                        indexed_file = self._process_file(full_path, filename, ext)
                        if indexed_file:
                            indexed_files.append(indexed_file)
                            count += 1
                    except Exception:
                        pass # Skip errors silently for cleaner UX

        self._index = indexed_files
        if progress_callback:
            progress_callback(f"Indexing complete: {count} files found.")
            
        return indexed_files

    def _process_file(self, path: str, name: str, ext: str) -> Optional[IndexedFile]:
        try:
            stats = os.stat(path)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(config.MAX_FILE_CHARS)
            
            tokens = content.lower().split()
            preview = content[:config.PREVIEW_CHARS].replace('\n', ' ').strip()
            if len(content) > config.PREVIEW_CHARS:
                preview += "..."

            return IndexedFile(
                path=path,
                name=name,
                extension=ext,
                size_bytes=stats.st_size,
                modified_time=stats.st_mtime,
                content=content,
                tokens=tokens,
                preview=preview
            )
        except Exception:
            return None

    def save_index(self, path: str) -> None:
        data = [f.as_dict() for f in self._index]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def load_index(self, path: str) -> List[IndexedFile]:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        self._index = []
        for item in data:
            content = item.get("content", "") or ""
            preview = item.get("preview", "") or (content[:config.PREVIEW_CHARS].replace("\n", " "))
            
            idx = IndexedFile(
                path=item.get("path", ""),
                name=item.get("name", ""),
                extension=item.get("extension", ""),
                size_bytes=item.get("size_bytes", 0),
                modified_time=item.get("modified_time", time.time()),
                content=content,
                tokens=content.lower().split() if content else [],
                preview=preview,
            )
            self._index.append(idx)

        return self._index
