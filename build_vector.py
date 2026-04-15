import json
from pathlib import Path
from src.embedding import embed_texts
from src.config import AUDIO_DIR, TRANSCRIPT_DIR
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = Path("data/chroma_db")
CHROMA_DIR.mkdir(exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(name="podcast")

def split_long_text(segments, max_chars=500):
    """把转录的碎片段 合并+切片 成适合向量化的文本块"""
    chunks = []
    current_text = ""
    current_start = 0

    for seg in segments:
        text = seg["text"].strip()
        start = seg["start"]
        end = seg["end"]

        if len(current_text + text) > max_chars:
            chunks.append({
                "text": current_text.strip(),
                "start": current_start,
                "end": end
            })
            current_text = text
            current_start = start
        else:
            current_text += " " + text
            if not current_start:
                current_start = start

    if current_text:
        chunks.append({
            "text": current_text.strip(),
            "start": current_start,
            "end": segments[-1]["end"]
        })

    return chunks

def process_all_transcripts():
    """批量处理所有 JSON → 切片 → 向量化 → 存入向量库"""
    json_files = list(TRANSCRIPT_DIR.glob("*.json"))
    print(f"🎯 找到 {len(json_files)} 个转录文件")

    for idx, json_path in enumerate(json_files, 1):
        print(f"\n===== [{idx}/{len(json_files)}] 处理：{json_path.name} =====")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. 文本切片
            chunks = split_long_text(data["segments"])
            texts = [c["text"] for c in chunks]

            # 2. 生成向量
            vecs = embed_texts(texts)

            # 3. 存入向量库
            ids = [f"{json_path.stem}-{i}" for i in range(len(chunks))]
            metadatas = [{
                "audio": data["audio_path"],
                "start": c["start"],
                "end": c["end"],
                "text": c["text"]
            } for c in chunks]

            collection.add(
                ids=ids,
                embeddings=vecs.tolist(),
                metadatas=metadatas
            )

            print(f"✅ 成功存入 {len(chunks)} 条向量")

        except Exception as e:
            print(f"❌ 失败：{e}")

    print("\n🎉🎉🎉 全部向量数据库构建完成！")
    print("📂 数据库位置：data/chroma_db/")

if __name__ == "__main__":
    process_all_transcripts()