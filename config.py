"""
config.py - Configuration settings
"""

PARALLAX_API_URL = "http://localhost:3001/v1/chat/completions"
PARALLAX_TIMEOUT = 120

PREVIEW_CHARS = 400
MAX_FILE_CHARS = 200_000

PARALLAX_SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Analyze the provided file candidates and select the ones that match the user's query. "
    "Return a JSON object with 'ranked' (list of file paths in order of relevance) and 'reasoning' (brief explanation)."
)

THEME = {
    "bg": "#000000",
    "panel_bg": "#1A1A1A",
    "glass": (30, 30, 30, 120),
    "glass_border": (255, 255, 255, 40),
    "text": "#FFFFFF",
    "text_dim": "#999999",
    "accent": "#00D9FF",
    "orb_blue": "#4169E1",
    "orb_orange": "#FF6B35",
    "orb_pink": "#FF1493",
}

FONT_FAMILY = "Segoe UI"

ALLOWED_EXTENSIONS = {'.txt', '.md', '.log', '.py', '.json', '.csv', '.js', '.html', '.css'}
