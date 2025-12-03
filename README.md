# File Finder

Local file search using semantic understanding and distributed model inference.

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [How to Use Search Modes](#how-to-use-search-modes)
- [System Design](#system-design)
- [Common Issues](#common-issues)
- [License](#license)
- [Stack](#stack)

## Problem

Finding relevant files when you know some context but not the exact filename is tedious:
- Keyword search misses files with synonyms or different phrasing
- Traditional tools don't understand intent
- Manual browsing through thousands of files is slow

## Solution

File Finder combines:
- **Local semantic search** — TF-IDF ranking to filter candidates
- **Distributed inference** — Uses Parallax to run models locally
- **Two search modes** — Choose between fast or comprehensive

## Features

- **Hybrid Search** — Semantic pre-filter + model ranking (faster)
- **Full AI Search** — Model searches all files (comprehensive)
- **File Indexing** — Scan, cache, and persist file indexes
- **GUI Application** — Cross-platform desktop interface
- **Batch Processing** — Efficiently handles large file sets

## Architecture

```
User Query
    ↓
[File Finder GUI]
    ↓
[Indexer]        [Search Engine]
    ↓                   ↓
[Cached Files] → [TF-IDF or Full Search]
                        ↓
                [Parallax API]
                        ↓
                [Results Display]
```

## How It Works

### Hybrid Search (Recommended)

1. **Semantic ranking** — TF-IDF scores all files against query
2. **Select top candidates** — Takes top 100 matches
3. **Model refinement** — Sends only these to Parallax
4. **Returns results** — Final ranked list with reasoning

**Use when:** You know some context about the file

### Full AI Search

1. **Batch splitting** — Divides files into chunks
2. **Parallel processing** — Sends multiple batches to model
3. **Merge results** — Combines and sorts all matches
4. **Returns results** — Complete ranking across all files

**Use when:** You want comprehensive search of all files

## Installation

### Requirements
- Python 3.8+
- Parallax cluster running locally
- wxPython, requests, scikit-learn

### Setup

1. **Clone repository:**
```bash
git clone https://github.com/LonelyGuy-SE1/file-finder.git
cd file-finder
```

2. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Start Parallax locally:**
```bash
parallax run
```

In another terminal, join as worker:
```bash
parallax join
```

5. **Verify endpoint:**
```bash
curl -X POST http://localhost:3001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}], "max_tokens": 100, "stream": true}'
```

Should return streaming response starting with `data: {...}`

6. **Run application:**
```bash
python ui_main.py
```

## Usage

1. **Select folder** — Click BROWSE to choose directory
2. **Index files** — Click INDEX to scan (shows progress)
3. **Type query** — Enter what you're looking for
4. **Choose search mode:**
   - **Hybrid Search** — Fast, uses semantic pre-filter
   - **Full AI Search** — Comprehensive, searches all files
5. **Review results** — Click to open matched files

### Save/Load Indexes

**Save:** Click SAVE INDEX to store current index
**Load:** Click LOAD INDEX to use saved index later

Useful for large datasets that take time to index.

## Configuration

Edit `config.py`:

```python
# Parallax endpoint
PARALLAX_API_URL = "http://localhost:3001/v1/chat/completions"
PARALLAX_TIMEOUT = 120

# Indexing
PREVIEW_CHARS = 400
MAX_FILE_CHARS = 200_000

# Supported file types
ALLOWED_EXTENSIONS = {'.txt', '.md', '.log', '.py', '.json', '.csv', '.js', '.html', '.css'}

# Theme
THEME = {
    "bg": "#000000",
    "panel_bg": "#1A1A1A",
    "text": "#FFFFFF",
    "text_dim": "#999999",
    "accent": "#00D9FF",
}
```

To customize search:
- Edit `batch_size` in `search_engine.py` for batching
- Edit `top_k` in `semantic_search()` for hybrid filtering
- Change `ALLOWED_EXTENSIONS` for file types

## How to Use Search Modes

### Hybrid Search

Use this when **you know something about the file** (context, keywords, partial path).

Example queries:
- "database connection code"
- "error handling"
- "user authentication"
- "config parsing"

The TF-IDF pre-filter catches semantically similar files, then model ranks them.

### Full AI Search

Use this when **you want to be thorough** and search everything.

Example scenarios:
- Important search where you can't miss results
- Small-to-medium datasets (< 50K files)
- Exploratory search with no context

The model sees all files, so it catches edge cases.

## System Design

### UI Layer
- File browsing and indexing controls
- Search input and mode selection
- Results display with click-to-open

### Application Core
- **FileIndexer** — Scans, reads, and caches files
- **SearchEngine** — Hybrid and full search logic with batching
- **ParallaxClient** — HTTP client for model inference

### Parallax Cluster
- Runs LLM locally (no cloud dependency)
- Handles distributed inference
- OpenAI-compatible API format

### Data Flow

**Hybrid:**
```
Query → TF-IDF ranking → Top 100 candidates → Parallax API → Results
```

**Full:**
```
Query → Batch splitting → Parallel API calls → Merge & sort → Results
```

## Common Issues

**Connection failed to Parallax**
- Check Parallax is running: `curl http://localhost:3001/v1/chat/completions`
- Restart: `parallax run` in one terminal, `parallax join` in another

**Search times out**
- Increase timeout in `config.py`: `PARALLAX_TIMEOUT = 300`
- Use Hybrid search instead of Full
- Check Parallax is responsive

**No results found**
- Ensure files match `ALLOWED_EXTENSIONS`
- Try Full search (Hybrid filters more aggressively)
- Check activity log for errors

## License

MIT License - See LICENSE file

## Stack

- **Parallax** — Distributed LLM serving
- **wxPython** — Cross-platform GUI
- **scikit-learn** — TF-IDF vectorization
- **Qwen/Llama** — LLM models

---

Built for efficient local file discovery with AI assistance.
