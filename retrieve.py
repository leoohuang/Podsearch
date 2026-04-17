# retrieve.py
from src.search import search_with_rerank

def run_search():
    print("=" * 60)
    print("播客语义搜索系统")
    print("=" * 60)
    
    query = input("\n请输入搜索内容：")
    results = search_with_rerank(query)
    
    print("\n" + "="*60)
    print(f"🔍 搜索结果：{query}")
    print("="*60)
    
    for res in results:
        print(f"\n【第{res['rank']}名】,精排分数{res['rerank_score']:.3f} 相似度：{res['similarity']:.3f}")
        print(f"⏰ {res['start']:.2f}s ~ {res['end']:.2f}s")
        print(f"🎙️ 播客：{res['podcast_name']}")
        print(f"📄 {res['text'][:180]}...")
        print("-" * 60)
        

if __name__ == "__main__":
    run_search()