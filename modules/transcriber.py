import os
import json
import whisper

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-master-latest-win64-gpl-shared\bin"


def transcribe_video(video_path, output_folder="transcript"):

    print("Memuat Whisper...")
    model = whisper.load_model("base")

    print("Mentranskripsi video...")

    # word_timestamps=True -> berguna nanti kalau mau bikin caption
    # gaya TikTok (highlight per kata)
    result = model.transcribe(video_path, word_timestamps=True, verbose=True)

    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, "transcript.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result["segments"], f, ensure_ascii=False, indent=4)

    print(f"✅ Transcript disimpan di {output_file}")

    return output_file