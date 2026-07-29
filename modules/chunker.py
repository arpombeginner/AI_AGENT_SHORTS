import os

from config import (
    CLEAN_TRANSCRIPT,
    CHUNK_FOLDER,
    MAX_CHARS
)


def chunk_transcript():

    os.makedirs(CHUNK_FOLDER, exist_ok=True)

    # Bersihkan chunk lama biar tidak numpuk / kecampur video sebelumnya
    for old_file in os.listdir(CHUNK_FOLDER):
        if old_file.endswith(".txt"):
            os.remove(os.path.join(CHUNK_FOLDER, old_file))

    with open(CLEAN_TRANSCRIPT, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []

    current_chunk = ""

    for line in text.splitlines():

        if len(current_chunk) + len(line) < MAX_CHARS:

            current_chunk += line + "\n"

        else:

            chunks.append(current_chunk)

            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    for i, chunk in enumerate(chunks):

        filename = os.path.join(
            CHUNK_FOLDER,
            f"chunk_{i+1:03}.txt"
        )

        with open(filename, "w", encoding="utf-8") as f:

            f.write(chunk)

    print(f"✅ {len(chunks)} chunk berhasil dibuat.")