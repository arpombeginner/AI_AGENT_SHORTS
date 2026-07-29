import os
import yt_dlp


def download_video(url):

    output_path = "input/video.mp4"

    # Hapus video lama dulu, biar tidak ke-skip / ketuker sama video sebelumnya
    if os.path.exists(output_path):
        os.remove(output_path)

    ydl_opts = {
        "format": "best",
        "outtmpl": output_path,
        "overwrites": True,
        "nooverwrites": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("✅ Download selesai!")