import json
import textwrap


def format_srt_time(seconds):
    """
    Konversi detik (float) ke format waktu SRT: HH:MM:SS,mmm
    """

    if seconds < 0:
        seconds = 0

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def wrap_caption(text, max_chars=40):
    """
    Pecah teks panjang jadi maksimal 2 baris biar caption tidak
    kepanjangan satu baris.
    """

    wrapped = textwrap.wrap(text, width=max_chars, max_lines=2, placeholder="...")
    return "\n".join(wrapped)


def load_segments(transcript_json_path):

    with open(transcript_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_srt_for_clip(transcript_json_path, start_sec, end_sec, output_srt_path):
    """
    Ambil segmen transcript yang overlap dengan rentang [start_sec, end_sec],
    lalu tulis jadi file .srt dengan waktu yang sudah di-offset relatif
    ke awal clip (supaya sinkron dengan video hasil potongan).
    """

    entries = get_caption_entries(transcript_json_path, start_sec, end_sec)

    with open(output_srt_path, "w", encoding="utf-8") as f:

        for i, (start, end, text) in enumerate(entries, start=1):

            f.write(f"{i}\n")
            f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
            f.write(f"{wrap_caption(text)}\n\n")

    return output_srt_path


def get_caption_entries(transcript_json_path, start_sec, end_sec):
    """
    Sama seperti generate_srt_for_clip, tapi mengembalikan data mentah
    (list of tuple: start, end, text) relatif ke awal clip, tanpa nulis
    file .srt. Dipakai untuk pendekatan drawtext per-baris.
    """

    segments = load_segments(transcript_json_path)

    entries = []

    for seg in segments:

        seg_start = seg["start"]
        seg_end = seg["end"]
        text = seg["text"].strip()

        if not text:
            continue

        if seg_end <= start_sec or seg_start >= end_sec:
            continue

        clipped_start = max(seg_start, start_sec) - start_sec
        clipped_end = min(seg_end, end_sec) - start_sec

        if clipped_end <= clipped_start:
            continue

        entries.append((clipped_start, clipped_end, text))

    return entries