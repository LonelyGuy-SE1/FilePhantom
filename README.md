# File Phantom (Local File Search)

Local file search using semantic understanding and distributed model inference.

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Why Parallax](#why-parallax-?)
- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [How to Use Search Modes](#how-to-use-search-modes)
- [System Design](#system-design)
- [Demo & Screenshots](#demo--screenshots)
- [License](#license)


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

## Why Parallax ?
- Privacy, while dealing with files on local systems, privacy is paramount and hence in this use case, the AI model would have to run locally to preserve the privacy of the user.
- Parallel Execution in order to decrease search time in the best interest of the user.
- Flexibility to modify various parameters based on the users desire. (Model, Token Limits, Etc.)

## Features

- **Hybrid Search** — Semantic pre-filter + model ranking (faster)
- **Full AI Search** — Model searches all files (comprehensive) (Parallel Execution is implemented in order to improve search speed. You can change the number of batches/batch size based on the capacity of your cluster to further speed up the process)
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
                [LLM running on Parallax]
                        ↓
                [Results Display]
```

## How It Works

### Hybrid Search (Recommended)

1. **Semantic ranking** — TF-IDF scores all files against query
2. **Select top candidates** — Takes top 100 matches (Can Be changed)
3. **Model refinement** — Sends only these to Parallax
4. **Returns results** — Final ranked list with reasoning

**Use when:** You know some context about the file (required for the initial semantic search).

### Full AI Search

1. **Batch splitting** — Divides files into chunks
2. **Parallel processing** — Sends multiple batches to model
3. **Merge results** — Combines and sorts all matches
4. **Returns results** — Complete ranking across all files

**Use when:** You want comprehensive search of all files and are not sure of the exact semantics used in the file.

## Installation

### Requirements

- Python 3.8+
- Parallax cluster running locally
- wxPython, requests, scikit-learn

### Setup

1. **Clone repository:**

```bash
git https://github.com/LonelyGuy-SE1/FilePhantom.git
cd FilePhantom
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

Refer to [Parallax Setup](https://github.com/GradientHQ/parallax/blob/main/docs/user_guide/quick_start.md)

5. **Run application:**

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
The TF-IDF pre-filter catches semantically similar files, then model ranks them.

### Full AI Search

Use this when **you want to be thorough** and search everything.
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

## License

MIT License - See LICENSE file

## Demo & Screenshots

Initial GUI
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/5acd9fd5-9c5d-4028-82ae-a5af51bd0785" />

After browsing the desired folder and indexing.
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/54b11170-4405-4aeb-b55a-6f3c3ea85226" />

After a Hybrid Search.
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/698225f5-95bb-4c31-b6bc-3859624b2803" />

After a Full AI Aearch.
<img width="1366" height="767" alt="image" src="https://github.com/user-attachments/assets/cde00efd-5910-46b9-878b-8ab6fa2db08b" />


### Workflow

1. **Start Application** → GUI window opens
2. **Select Folder** → Click BROWSE and choose directory
3. **Index Files** → Click INDEX, watch progress bar
4. **Type Query** → Enter natural language search
5. **Choose Mode** → Click Hybrid (fast) or Full (comprehensive)
6. **Review Results** → See ranked matches with explanations
7. **Open File** → Click any result to open in default app

Built for efficient local file discovery with AI assistance.
