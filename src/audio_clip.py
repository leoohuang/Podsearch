from pydub import AudioSegment
import hashlib
import os

CLIP_DIR = "data/clips"
os.makedirs(CLIP_DIR, exist_ok=True)

def get_audio_clip(audio_path, start_sec, end_sec):
    # 1. 生成缓存文件名（同样的片段不重复切）
    key = hashlib.md5(f"{audio_path}{start_sec}{end_sec}".encode()).hexdigest()
    cache_path = os.path.join(CLIP_DIR, f"{key}.mp3")

    # 2. 如果之前切过，直接返回
    if os.path.exists(cache_path):
        return cache_path

    # 3. 加载完整音频，切出片段（前后各多留3秒）
    audio = AudioSegment.from_file(audio_path)
    start_ms = max(0, int((start_sec - 3) * 1000))
    end_ms = int((end_sec + 3) * 1000)
    clip = audio[start_ms:end_ms]

    # 4. 保存并返回路径
    clip.export(cache_path, format="mp3")
    return cache_path