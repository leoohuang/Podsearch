from pathlib import Path  # 自带的工具，专门处理文件路径

ROOT = Path(__file__).parent.parent  
# 意思：找到【当前 config.py 文件】的【上上级目录】→ 就是项目根文件夹 podsearch/


DATA_DIR = ROOT / "data"        # 项目根目录下的 data 文件夹
AUDIO_DIR = DATA_DIR / "raw_audio"  # 下载的播客音频存在这
TRANSCRIPT_DIR = DATA_DIR / "transcripts"  # 语音转文字的结果存在这
CHUNK_DIR = DATA_DIR / "chunks"  # 切分好的文本片段存在这
CHROMA_DIR = DATA_DIR / "chroma_db"  # 向量数据库存在这

#whisper配置
WHISPER_MODEL = "large-v3"   # 用最大最强的模型
WHISPER_DEVICE = "cpu"       # Mac 目前只能用 CPU 跑（够用）
WHISPER_COMPUTE = "int8"     # 压缩计算，更快、更省内存


#Embedding 配置
EMBED_MODEL = "BAAI/bge-m3"       # 目前最强的开源 embedding 模型
EMBED_DIM = 1024                  # 向量维度（固定不用改）
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"  # 搜索后重排，让结果更准

#chunking配置
CHUNK_MIN_SEC = 30    # 每段至少 30 秒
CHUNK_MAX_SEC = 60    # 每段最多 60 秒
CHUNK_OVERLAP_SEC = 5 # 段落之间重叠 5 秒，防止语义断开

#search配置
TOP_K_RETRIEVE = 30   # 先从库里找 30 条最相关的
TOP_K_RERANK = 10     # 重排后，只返回最准的 10 条  