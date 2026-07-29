
from modules.downloader import download_video
from modules.transcriber import transcribe_video
from modules.cleaner import clean_transcript
from modules.chunker import chunk_transcript
from modules.analyzer import analyze_chunks
from modules.cutter import cut_clips
 
url = input("Masukkan Link YouTube: ")
 
# 1. Download video
download_video(url)
 
# 2. Transkripsi
transcribe_video("input/video.mp4")
 
# 3. Bersihkan transcript
clean_transcript()
 
# 4. Bagi menjadi beberapa chunk
chunk_transcript()
 
# 5. Analisis setiap chunk menggunakan AI
analyze_chunks()
 
# 6. Potong video jadi Shorts berdasarkan hasil analisis
cut_clips() 