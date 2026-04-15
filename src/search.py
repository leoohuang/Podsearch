# src/search.py 最终完美版 ✅
from src.indexing import get_collection
from src.embedding import embed_texts
import os

def search(query: str, top_k: int = 10):
    query_vec = embed_texts([query])[0]
    col = get_collection()
    
    results = col.query(
        query_embeddings=[query_vec.tolist()],
        n_results=top_k,
        include=["metadatas", "distances"]
    )
    
    return format_results(results)

def format_results(results):
    formatted = []
    for i, meta in enumerate(results["metadatas"][0]):
        dist = results["distances"][0][i]
        audio_path = meta.get("audio", "")

        # ===========================
        # 自动提取播客名
        # ===========================
        podcast_name = "未知播客"
        try:
            # 直接取音频所在的文件夹名 = 播客名
            folder = os.path.basename(os.path.dirname(audio_path))
            podcast_name = folder.replace("_", " ")  # 下划线变空格
        except:
            pass

        formatted.append({
            "rank": i + 1,
            "similarity": 1 - dist,
            "start": meta.get("start"),
            "end": meta.get("end"),
            "text": meta.get("text", ""),
            "audio_file": audio_path,
            "podcast_name": podcast_name
        })
    return formatted