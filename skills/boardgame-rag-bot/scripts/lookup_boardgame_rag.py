#!/usr/bin/env python3
"""Lookup a private board-game RAG index with hybrid semantic + lexical search."""
from __future__ import annotations

import argparse
import json
import math
import pickle
import re
from pathlib import Path
from typing import Dict, List, Tuple

WORD_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "you", "your", "are", "can", "how", "what", "when", "does",
    "into", "from", "about", "have", "has", "was", "were", "its", "all", "any", "one", "two", "page", "rule",
}


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text) if len(t.strip()) > 1]


def query_terms(text: str) -> List[str]:
    terms = [t for t in tokenize(text) if t not in STOPWORDS]
    return terms or tokenize(text)


def load_index(index_dir: Path) -> Tuple[List[Dict], Dict]:
    manifest_path = index_dir / "manifest.json"
    chunks_path = index_dir / "chunks.jsonl"
    if not manifest_path.exists() or not chunks_path.exists():
        raise SystemExit(f"Index not found at {index_dir}. Run build_boardgame_rag.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return chunks, manifest


def bm25_score(chunk: Dict, terms: List[str], manifest: Dict) -> float:
    tf = chunk.get("term_freq", {})
    n_docs = max(1, int(manifest.get("chunk_count", 1)))
    avg_len = float(manifest.get("avg_chunk_length", 1.0)) or 1.0
    doc_len = float(chunk.get("length", 1)) or 1.0
    df = manifest.get("doc_freq", {})
    k1, b = 1.4, 0.72
    score = 0.0
    heading = (chunk.get("heading") or "").lower()
    excerpt = (chunk.get("excerpt") or "").lower()
    for term in terms:
        f = float(tf.get(term, 0))
        if f <= 0:
            continue
        term_df = float(df.get(term, 0))
        idf = math.log(1.0 + (n_docs - term_df + 0.5) / (term_df + 0.5))
        denom = f + k1 * (1.0 - b + b * doc_len / avg_len)
        score += idf * (f * (k1 + 1.0) / denom)
        if term in heading:
            score += idf * 1.25
        if term in excerpt:
            score += idf * 0.15
    phrase = " ".join(terms)
    if len(terms) > 1 and phrase in f"{heading} {excerpt}":
        score += 2.0
    return score


def semantic_scores(index_dir: Path, manifest: Dict, query: str) -> Dict[int, float]:
    sem = manifest.get("semantic") or {}
    if not sem.get("available"):
        return {}
    try:
        import numpy as np  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception:
        return {}
    emb_path = index_dir / str(sem.get("path") or "embeddings.npy")
    if not emb_path.exists():
        return {}
    model = SentenceTransformer(sem.get("model") or "sentence-transformers/all-MiniLM-L6-v2")
    q = model.encode([query], normalize_embeddings=True)[0]
    matrix = np.load(emb_path)
    sims = matrix @ q
    return {i: float(s) for i, s in enumerate(sims)}


def tfidf_scores(index_dir: Path, query: str) -> Dict[int, float]:
    p = index_dir / "vectorizer.pkl"
    if not p.exists():
        return {}
    try:
        with p.open("rb") as f:
            data = pickle.load(f)
        q = data["vectorizer"].transform([query])
        sims = (data["matrix"] @ q.T).toarray().ravel()
        return {i: float(s) for i, s in enumerate(sims)}
    except Exception:
        return {}


def rrf_merge(rankings: List[List[int]], k: int = 60) -> Dict[int, float]:
    scores: Dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking, start=1):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + rank)
    return scores


def make_result(chunk: Dict, score: float, match_type: str, semantic: float | None, lexical: float | None) -> Dict:
    return {
        "source": chunk.get("source"),
        "page": chunk.get("page"),
        "heading": chunk.get("heading"),
        "score": round(score, 6),
        "semantic_score": None if semantic is None else round(semantic, 6),
        "lexical_score": None if lexical is None else round(lexical, 6),
        "match_type": match_type,
        "excerpt": chunk.get("excerpt", ""),
        "anchor": chunk.get("anchor"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Lookup board-game rules in a local semantic RAG index")
    ap.add_argument("query", nargs="+", help="Search query")
    ap.add_argument("--index-dir", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--source", help="Optional case-insensitive source substring filter, e.g. 'FAQ' or 'Expansion'")
    ap.add_argument("--mode", choices=["hybrid", "semantic", "lexical"], default="hybrid")
    args = ap.parse_args()

    query = " ".join(args.query).strip()
    chunks, manifest = load_index(args.index_dir)
    if args.source:
        needle = args.source.lower()
        keep = [(i, c) for i, c in enumerate(chunks) if needle in str(c.get("source", "")).lower()]
    else:
        keep = list(enumerate(chunks))
    if not keep:
        print(json.dumps({"query": query, "count": 0, "results": [], "warning": "source filter matched no chunks"}, indent=2))
        return 0

    terms = query_terms(query)
    sem_all = semantic_scores(args.index_dir, manifest, query) if args.mode in ("hybrid", "semantic") else {}
    tfidf_all = tfidf_scores(args.index_dir, query) if args.mode in ("hybrid", "lexical") else {}
    bm25_all = {i: bm25_score(c, terms, manifest) for i, c in keep} if args.mode in ("hybrid", "lexical") else {}

    rankings: List[List[int]] = []
    if sem_all:
        rankings.append([i for i, _ in sorted(((i, sem_all.get(i, 0.0)) for i, _ in keep), key=lambda x: -x[1]) if sem_all.get(i, 0.0) > 0])
    if tfidf_all:
        rankings.append([i for i, _ in sorted(((i, tfidf_all.get(i, 0.0)) for i, _ in keep), key=lambda x: -x[1]) if tfidf_all.get(i, 0.0) > 0])
    if bm25_all:
        rankings.append([i for i, _ in sorted(bm25_all.items(), key=lambda x: -x[1]) if bm25_all.get(i, 0.0) > 0])

    fused = rrf_merge(rankings) if rankings else {}
    chunk_by_i = dict(keep)
    ranked = sorted(fused.items(), key=lambda x: (-x[1], str(chunk_by_i[x[0]].get("source", "")), chunk_by_i[x[0]].get("page") or 0))
    results = []
    for i, fused_score in ranked[: max(1, args.limit)]:
        sem = sem_all.get(i)
        lex = max(tfidf_all.get(i, 0.0), bm25_all.get(i, 0.0)) if (tfidf_all or bm25_all) else None
        mt = "hybrid" if sem is not None and lex is not None else "semantic" if sem is not None else "lexical"
        results.append(make_result(chunk_by_i[i], fused_score, mt, sem, lex))

    print(json.dumps({
        "query": query,
        "terms": terms,
        "mode": args.mode,
        "semantic_available": bool(sem_all),
        "lexical_available": bool(tfidf_all or bm25_all),
        "count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
