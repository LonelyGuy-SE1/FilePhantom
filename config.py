"""
config.py
Configuration settings for the Parallax File Finder.
"""

PARALLAX_API_URL = "http://localhost:3001/v1/chat/completions"
PARALLAX_TIMEOUT = 120

PREVIEW_CHARS = 400
MAX_FILE_CHARS = 200_000

PARALLAX_SYSTEM_PROMPT = (
    "You are an intelligent file search agent. "
    "Your task is to analyze the provided file candidates and select the ones that are relevant to the user's query. "
    "You must understand the user's intent and the content of the files. "
    "Return a JSON object with two keys: "
    "1. 'ranked': A list of file IDs (paths) for the matching files, ordered by relevance. Exclude irrelevant files. "
    "2. 'reasoning': A concise explanation of why these files were selected and how they match the query."
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
