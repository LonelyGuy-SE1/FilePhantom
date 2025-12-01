"""
config.py
Configuration settings for the Parallax File Finder.
"""

# API Settings
PARALLAX_API_URL = "http://localhost:3001/v1/chat/completions"
PARALLAX_TIMEOUT = 120

# Search Settings
TOP_K_CANDIDATES = 20
PREVIEW_CHARS = 400
MAX_FILE_CHARS = 200_000

# System Prompt
PARALLAX_SYSTEM_PROMPT = (
    "You are a helpful file search assistant. "
    "Your task is to re-rank the provided file candidates based on how well they match the user's query. "
    "Return a JSON object with a 'ranked' key containing a list of file IDs (paths) in order of relevance, "
    "and a 'reasoning' key explaining why."
)

# Theme: Minimal Glassmorphism
THEME = {
    "bg": "#000000",
    "panel_bg": "#1A1A1A",              # Fallback for glass panels
    "glass": (30, 30, 30, 120),
    "glass_border": (255, 255, 255, 40),
    "text": "#FFFFFF",
    "text_dim": "#999999",
    "accent": "#00D9FF",
    
    "orb_blue": "#4169E1",
    "orb_orange": "#FF6B35",
    "orb_pink": "#FF1493",
}

# Fonts
FONT_FAMILY = "Segoe UI"

# Indexer
ALLOWED_EXTENSIONS = {'.txt', '.md', '.log', '.py', '.json', '.csv', '.js', '.html', '.css'}
