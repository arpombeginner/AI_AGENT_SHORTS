import os
import re
import json
import subprocess
import textwrap

from config import (
    FFMPEG_PATH,
    VIDEO_FILE,
    OUTPUT_FOLDER,
    CLIPS_JSON,
    TRANSCRIPT_JSON
)

from modules.subtitler import get_caption_entries


SCORE_THRESHOLD = 8.0
SHORTS_FOLDER = os.path.join(OUTPUT_FOLDER, "shorts")

# Ganti path ini kalau font-nya tidak ada di komputer kamu.
# Cek folder C:\Windows\Fonts untuk lihat font yang tersedia.
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"

# Output vertikal standar Shorts/Reels/TikTok
OUT_WIDTH = 1080
OUT_HEIGHT = 1920


def time_to_seconds(time_str):

    parts = time_str.strip().split(":")
    parts = [int(p) for p in parts]

    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds

    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds

    raise ValueError(f"Format waktu tidak dikenali: {time_str}")


def slugify(text):

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:60]


def escape_for_filter(path):
    """
    ffmpeg filter_complex butuh path dengan format khusus:
    backslash -> forward slash, dan titik dua drive (C:) di-escape.
    """

    path = path.replace("\\", "/")
    path = path.replace(":", "\\:")
    return path


def wrap_title(title, max_chars=20):
    lines = textwrap.wrap(title, width=max_chars, max_lines=3, placeholder="...")
    return "\n".join(lines)


def load_clips():

    with open(CLIPS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    clips = []

    for item in data:

        result = item.get("result")

        if not isinstance(result, dict):
            print(f"⚠️  Lewati {item.get('chunk')}: result bukan JSON valid.")
            continue

        required_keys = ["score", "title", "start_time", "end_time"]

        if not all(k in result for k in required_keys):
            print(f"⚠️  Lewati {item.get('chunk')}: field tidak lengkap.")
            continue

        clips.append(result)

    return clips


def select_clips(clips):

    selected = [c for c in clips if c["score"] >= SCORE_THRESHOLD]

    if not selected and clips:
        best = max(clips, key=lambda c: c["score"])
        selected = [best]
        print(
            f"ℹ️  Tidak ada clip dengan score >= {SCORE_THRESHOLD}. "
            f"Fallback ke skor tertinggi: '{best['title']}' ({best['score']})"
        )

    return selected


def render_clip(index, clip):

    start_sec = time_to_seconds(clip["start_time"])
    end_sec = time_to_seconds(clip["end_time"])
    duration = end_sec - start_sec

    if duration <= 0:
        print(f"⚠️  Durasi tidak valid untuk '{clip['title']}', dilewati.")
        return None

    base_name = f"{index+1:02}_{slugify(clip['title'])}"
    output_path = os.path.join(SHORTS_FOLDER, base_name + ".mp4")
    title_txt_path = os.path.join(SHORTS_FOLDER, base_name + "_title.txt")

    # 1. Ambil data caption (start, end, text) relatif ke awal clip
    caption_entries = get_caption_entries(TRANSCRIPT_JSON, start_sec, end_sec)

    # 2. Tulis tiap baris caption ke file .txt terpisah (hindari escaping)
    caption_files = []
    for i, (cap_start, cap_end, text) in enumerate(caption_entries):
        cap_txt_path = os.path.join(SHORTS_FOLDER, f"{base_name}_cap{i}.txt")
        wrapped = textwrap.wrap(text, width=35, max_lines=2, placeholder="...")
        with open(cap_txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(wrapped))
        caption_files.append((cap_start, cap_end, cap_txt_path))

    # 3. Tulis judul ke file teks terpisah (hindari masalah escaping karakter)
    wrapped_title = wrap_title(clip["title"])
    with open(title_txt_path, "w", encoding="utf-8") as f:
        f.write(wrapped_title)

    ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg.exe")

    font_filter_path = escape_for_filter(FONT_PATH)
    title_filter_path = escape_for_filter(title_txt_path)

    filter_complex = (
        f"[0:v]scale={OUT_WIDTH}:{OUT_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={OUT_WIDTH}:{OUT_HEIGHT},boxblur=25:25[bg];"

        f"[0:v]scale={OUT_WIDTH}:-2[fg];"

        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[merged];"

        f"[merged]drawtext=fontfile='{font_filter_path}':"
        f"textfile='{title_filter_path}':"
        f"fontsize=64:fontcolor=white:borderw=4:bordercolor=black:"
        f"x=(w-text_w)/2:y=100:line_spacing=10[titled]"
    )

    # 4. Rantai drawtext untuk tiap baris caption, tampil sesuai waktunya
    last_label = "titled"
    for i, (cap_start, cap_end, cap_txt_path) in enumerate(caption_files):

        cap_filter_path = escape_for_filter(cap_txt_path)
        next_label = f"cap{i}"

        filter_complex += (
            f";[{last_label}]drawtext=fontfile='{font_filter_path}':"
            f"textfile='{cap_filter_path}':"
            f"fontsize=42:fontcolor=white:borderw=3:bordercolor=black:"
            f"box=1:boxcolor=black@0.5:boxborderw=15:"
            f"x=(w-text_w)/2:y=h-350:line_spacing=8:"
            f"enable='between(t,{cap_start:.3f},{cap_end:.3f})'[{next_label}]"
        )

        last_label = next_label

    filter_complex += f";[{last_label}]copy[final]"

    cmd = [
        ffmpeg_exe,
        "-y",
        "-ss", str(start_sec),
        "-i", VIDEO_FILE,
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-map", "0:a:0?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-avoid_negative_ts", "make_zero",
        output_path
    ]

    print(f"✂️  Merender '{clip['title']}' ({clip['start_time']} - {clip['end_time']})")

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        print(f"❌ Gagal merender clip: {clip['title']}")
        print(result.stderr.decode(errors="ignore")[-2000:])
        return None

    print(f"✅ Tersimpan: {output_path}")
    return output_path


def cut_clips():

    os.makedirs(SHORTS_FOLDER, exist_ok=True)

    # Bersihkan hasil shorts dari video sebelumnya
    for old_file in os.listdir(SHORTS_FOLDER):
        old_path = os.path.join(SHORTS_FOLDER, old_file)
        if os.path.isfile(old_path):
            os.remove(old_path)

    clips = load_clips()

    if not clips:
        print("⚠️  Tidak ada clip valid untuk dipotong.")
        return

    selected = select_clips(clips)

    print(f"🎬 {len(selected)} clip akan dirender dari {VIDEO_FILE}")

    for i, clip in enumerate(selected):
        render_clip(i, clip)

    print("✅ Proses rendering Shorts selesai.")