from FlagEmbedding import FlagReranker
from src.indexing import get_collection
from src.embedding import embed_texts
import os
from src.config import RERANKER_MODEL

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        print("Loading reranker model...")
        _reranker = FlagReranker(RERANKER_MODEL, use_fp16=True)
    return _reranker

def search_with_rerank(query, retrieve_k=30, final_k=10):
    # 第一步：用向量搜索先捞出30条候选
    candidates = search(query, top_k=retrieve_k)

    if not candidates:
        return []

    # 第二步：把query和每条候选文本配对
    pairs = [(query, c["text"]) for c in candidates]

    # 第三步：cross-encoder给每对打分
    reranker = get_reranker()
    scores = reranker.compute_score(pairs, normalize=True)

    # 第四步：按新分数重新排序，取前10
    for c, s in zip(candidates, scores):
        c["rerank_score"] = s

    ranked = sorted(candidates, key=lambda x: -x["rerank_score"])

    for i, item in enumerate(ranked[:final_k]):
        item["rank"] = i + 1

    return ranked[:final_k]

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