from modules.cutter import cut_clips
 
# Script ini cuma jalanin proses render Shorts (cutter.py),
# pakai transcript.json dan clips.json yang sudah ada dari run sebelumnya.
# Jadi tidak perlu download + transcribe + analyze ulang -> jauh lebih cepat buat testing.
 
cut_clips()