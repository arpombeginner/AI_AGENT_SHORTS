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
Kamu adalah editor YouTube profesional.

Analisis transcript berikut. Transcript ini memiliki timestamp asli
dalam format [MM:SS - MM:SS] di atas setiap baris teks.

Tentukan SATU bagian yang PALING cocok dijadikan YouTube Shorts.

WAJIB gunakan timestamp ASLI yang ada di transcript (jangan menebak
atau mengarang waktu). start_time dan end_time harus persis sama
dengan salah satu timestamp yang muncul di transcript, atau gabungan
beberapa timestamp yang berurutan.

Durasi (end_time - start_time) idealnya antara 20 - 60 detik, cocok
untuk format YouTube Shorts.

Berikan jawaban HANYA dalam format JSON murni, TANPA markdown code
fence, TANPA teks tambahan apapun sebelum atau sesudah JSON.

Format wajib:
{
  "score": 9.8,
  "title": "Judul Shorts",
  "start_time": "02:04",
  "end_time": "02:32",
  "reason": "Alasan mengapa bagian ini menarik."
}

Transcript:

"""


def extract_json(raw_text):
    """
    Membersihkan output Gemini dari markdown code fence (```json ... ```)
    kalau ada, lalu parse jadi dict Python.
    """

    text = raw_text.strip()

    # Hapus code fence ```json ... ``` atau ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️  Gagal parse JSON: {e}")
        print(f"Raw text: {raw_text}")
        return None


def analyze_chunks():

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    hasil = []

    files = sorted(os.listdir(CHUNK_FOLDER))

    for file in files:

        if not file.endswith(".txt"):
            continue

        print(f"🔍 Menganalisis {file}")

        with open(
            os.path.join(CHUNK_FOLDER, file),
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read()

        prompt = PROMPT + text

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        parsed = extract_json(response.text)

        hasil.append({
            "chunk": file,
            "result": parsed if parsed is not None else response.text
        })

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