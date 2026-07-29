import os
from dotenv import load_dotenv

# ==========================
# LOAD ENV
# ==========================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================
# FFMPEG
# ==========================
FFMPEG_PATH = r"C:\ffmpeg-master-latest-win64-gpl-shared\bin"

# ==========================
# AI MODEL
# ==========================
WHISPER_MODEL = "base"

# Model Gemini
GEMINI_MODEL = "gemini-flash-latest"

# ==========================
# FOLDER
# ==========================
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
TEMP_FOLDER = "temp"
TRANSCRIPT_FOLDER = "transcript"
CHUNK_FOLDER = "chunks"

# ==========================
# FILE
# ==========================
VIDEO_FILE = f"{INPUT_FOLDER}/video.mp4"

TRANSCRIPT_JSON = f"{TRANSCRIPT_FOLDER}/transcript.json"
CLEAN_TRANSCRIPT = f"{TRANSCRIPT_FOLDER}/clean_transcript.txt"

CLIPS_JSON = f"{OUTPUT_FOLDER}/clips.json"

# ==========================
# CHUNK
# ==========================
MAX_CHARS = 3500