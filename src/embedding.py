from FlagEmbedding import BGEM3FlagModel
import numpy as np

_model = None

def get_embedder():
    global _model
    if _model is None:
        print("Loading BGE-M3 vector model...")
        _model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True) #for Mac
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    """
    transfor text into 1024 dimentional vectos
    return shape(text number, 1024) matrix
    """
    model = get_embedder()
    
    output = model.encode(
        texts,
        batch_size=32,    # Mac 16G 内存用 32 刚刚好
        max_length=512,   # 模型最大支持长度
        return_dense=True,
    )
    
    return output['dense_vecs']