import json
import os

def format_time(seconds):
    menit = int(seconds // 60)
    detik = int(seconds % 60)
    return f"{menit:02d}:{detik:02d}"

def clean_transcript(
    input_file="transcript/transcript.json",
    output_file="transcript/clean_transcript.txt"
):

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:

        for seg in data:

            start = format_time(seg["start"])
            end = format_time(seg["end"])
            text = seg["text"].strip()

            if text:

                f.write(f"[{start} - {end}]\n")
                f.write(text + "\n\n")

    print("✅ Clean transcript selesai.")