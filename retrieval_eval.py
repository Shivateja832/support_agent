"""Evaluate RAG retrieval and answer grounding quality.
Run: python retrieval_eval.py
"""
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from src.agent import SupportAgent

load_dotenv()

DATA = Path(__file__).parent / "data" / "qa_pairs.jsonl"
RESULTS = Path(__file__).parent / "data" / "retrieval_eval_results.json"


def load_qa_pairs(path: Path):
    pairs = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pairs.append(json.loads(line))
    return pairs


def main():
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERR] ANTHROPIC_API_KEY not set")
        return

    print("[INFO] Initializing agent...")
    agent = SupportAgent(api_key=api_key)
    
    pairs = load_qa_pairs(DATA)
    results = []
    
    print(f"[INFO] Evaluating {len(pairs)} QA pairs...\n")
    
    for p in pairs:
        qid = p.get("id")
        query = p.get("query")
        expected_source = p.get("expected_source")
        expected_keyword = p.get("expected_answer")
        
        # Retrieve
        hits = agent.vector_store.retrieve(query, top_k=5)
        
        # Check if expected source is in top-k
        source_match = any(h["source"] == expected_source for h in hits)
        
        # Check if expected keyword is in top hit
        keyword_in_response = False
        if hits and expected_keyword:
            keyword_in_response = expected_keyword.lower() in hits[0]["text"].lower()
        
        best_score = max((h["score"] for h in hits), default=0)
        
        result = {
            "id": qid,
            "query": query,
            "expected_source": expected_source,
            "top_source": hits[0]["source"] if hits else "N/A",
            "source_match": source_match,
            "best_retrieval_score": round(best_score, 4),
            "keyword_in_top_hit": keyword_in_response,
            "hits": len(hits),
        }
        results.append(result)
        
        status = "[OK]" if (source_match and keyword_in_response) else "[WARN]"
        print(f"{status} Q{qid}: '{query[:50]}...'")
        print(f"   Source: {expected_source} -> {result['top_source']} {'[yes]' if source_match else '[no]'}")
        print(f"   Score: {best_score:.3f}, Keyword: {'[yes]' if keyword_in_response else '[no]'}\n")
    
    # Summary
    source_hits = sum(1 for r in results if r["source_match"])
    keyword_hits = sum(1 for r in results if r["keyword_in_top_hit"])
    both_hits = sum(1 for r in results if r["source_match"] and r["keyword_in_top_hit"])
    avg_score = sum(r["best_retrieval_score"] for r in results) / len(results)
    
    summary = {
        "total_queries": len(results),
        "source_match_accuracy": round(source_hits / len(results) * 100, 1),
        "keyword_accuracy": round(keyword_hits / len(results) * 100, 1),
        "both_match_accuracy": round(both_hits / len(results) * 100, 1),
        "avg_retrieval_score": round(avg_score, 4),
        "details": results,
    }
    
    print(f"\n{'='*60}")
    print(f"[SUMMARY] Retrieval Evaluation")
    print(f"{'='*60}")
    print(f"Total Queries: {summary['total_queries']}")
    print(f"Source Match: {source_hits}/{len(results)} ({summary['source_match_accuracy']}%)")
    print(f"Keyword Match: {keyword_hits}/{len(results)} ({summary['keyword_accuracy']}%)")
    print(f"Both Correct: {both_hits}/{len(results)} ({summary['both_match_accuracy']}%)")
    print(f"Avg Retrieval Score: {summary['avg_retrieval_score']}")
    
    RESULTS.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n[OK] Results saved to {RESULTS}")


if __name__ == '__main__':
    main()
