import os
import json
import re

from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    CHUNK_FOLDER,
    OUTPUT_FOLDER,
    CLIPS_JSON
)

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = """
Kamu adalah editor YouTube Shorts profesional.

Berikut adalah transcript lengkap sebuah video.

Transcript memiliki timestamp asli dalam format:

[MM:SS - MM:SS]

Tugasmu:

1. Analisis seluruh transcript.
2. Pilih MAKSIMAL 3 bagian terbaik.
3. Jangan memilih bagian yang overlap.
4. Gunakan timestamp ASLI yang ada di transcript.
5. Durasi ideal 20-60 detik.
6. Prioritaskan bagian yang:
   - Hook kuat
   - Viral
   - Mengandung insight
   - Lucu
   - Emosional

Kembalikan HANYA JSON.

Format:

[
    {
        "score":9.8,
        "title":"Judul",
        "start_time":"02:04",
        "end_time":"02:38",
        "reason":"..."
    }
]

Transcript:

"""

def extract_json(text):

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()

    return json.loads(text)


def load_all_chunks():

    files = sorted(os.listdir(CHUNK_FOLDER))

    transcript = ""

    for file in files:

        if not file.endswith(".txt"):
            continue

        with open(
            os.path.join(CHUNK_FOLDER, file),
            "r",
            encoding="utf-8"
        ) as f:

            transcript += f.read()
            transcript += "\n\n"

    return transcript


def analyze_chunks():

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    transcript = load_all_chunks()

    print("🔍 Gemini sedang menganalisis seluruh video...")

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=PROMPT + transcript

    )

    hasil = extract_json(response.text)

    with open(

        CLIPS_JSON,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            hasil,

            f,

            indent=4,

            ensure_ascii=False

        )

    print("✅ Analisis selesai.")