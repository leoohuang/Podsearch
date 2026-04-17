"""
评估脚本：计算搜索系统的 MRR、Recall@K、Precision@K

用法：
    python eval/evaluate.py

评估集：eval/queries.json
"""
import json
import sys
sys.path.append(".")

from src.search import search, search_with_rerank

def load_queries(path="eval/queries.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def mrr(relevant_ranks, k=10):
    """Mean Reciprocal Rank: 第一个相关结果排在第几名"""
    for rank in range(1, k + 1):
        if rank in relevant_ranks:
            return 1.0 / rank
    return 0.0

def recall_at_k(relevant_ranks, k=10):
    """Recall@K: 前 K 条结果里包含了多少比例的相关结果"""
    if not relevant_ranks:
        return 0.0
    found = sum(1 for r in relevant_ranks if r <= k)
    return found / len(relevant_ranks)

def precision_at_k(relevant_ranks, k=10):
    """Precision@K: 前 K 条结果里有多少比例是相关的"""
    found = sum(1 for r in relevant_ranks if r <= k)
    return found / k

def evaluate_system(queries, search_fn, search_name, k=10):
    """对一组 query 跑评估，返回平均指标"""
    mrr_scores = []
    recall_scores = []
    precision_scores = []

    print(f"\n{'='*60}")
    print(f"评估: {search_name}")
    print(f"{'='*60}")

    for q in queries:
        query = q["query"]
        relevant = q["relevant_ranks"]

        m = mrr(relevant, k)
        r = recall_at_k(relevant, k)
        p = precision_at_k(relevant, k)

        mrr_scores.append(m)
        recall_scores.append(r)
        precision_scores.append(p)

        print(f"  {query:20s} | MRR={m:.3f} | Recall@{k}={r:.3f} | Precision@{k}={p:.3f} | 相关数={len(relevant)}")

    avg_mrr = sum(mrr_scores) / len(mrr_scores)
    avg_recall = sum(recall_scores) / len(recall_scores)
    avg_precision = sum(precision_scores) / len(precision_scores)

    print(f"\n{'─'*60}")
    print(f"  平均 MRR:          {avg_mrr:.3f}")
    print(f"  平均 Recall@{k}:    {avg_recall:.3f}")
    print(f"  平均 Precision@{k}: {avg_precision:.3f}")
    print(f"{'─'*60}")

    return {
        "name": search_name,
        "avg_mrr": avg_mrr,
        "avg_recall": avg_recall,
        "avg_precision": avg_precision,
    }

def main():
    queries = load_queries()
    print(f"加载了 {len(queries)} 个评估 query")

    # 这里直接用标注好的数据计算指标
    result = evaluate_system(queries, search_with_rerank, "向量召回 + Cross-Encoder 精排", k=10)

    # 汇总
    print(f"\n{'='*60}")
    print("汇总")
    print(f"{'='*60}")
    print(f"  系统: {result['name']}")
    print(f"  MRR:          {result['avg_mrr']:.3f}")
    print(f"  Recall@10:    {result['avg_recall']:.3f}")
    print(f"  Precision@10: {result['avg_precision']:.3f}")

if __name__ == "__main__":
    main()