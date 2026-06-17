#!/usr/bin/env python3
"""Query a local lexical index for Deep Rock Galactic board-game notes."""
from __future__ import annotations

import argparse
import json
import math
import os
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
        raise SystemExit(f"Index not found at {index_dir}. Run build_drg_index.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return chunks, manifest


def score_chunk(chunk: Dict, terms: List[str], manifest: Dict) -> float:
    tf = chunk.get("term_freq", {})
    n_docs = max(1, int(manifest.get("chunk_count", 1)))
    avg_len = float(manifest.get("avg_chunk_length", 1.0)) or 1.0
    doc_len = float(chunk.get("length", 1)) or 1.0
    df = manifest.get("doc_freq", {})
    k1 = 1.4
    b = 0.72
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
    q_phrase = " ".join(terms)
    if len(terms) > 1 and q_phrase in f"{heading} {excerpt}":
        score += 2.0
    return score


def make_result(chunk: Dict, score: float, include_path: bool) -> Dict:
    result = {
        "source": chunk.get("source"),
        "page": chunk.get("page"),
        "heading": chunk.get("heading"),
        "score": round(score, 4),
        "match_type": "lexical",
        "excerpt": chunk.get("excerpt", ""),
        "anchor": chunk.get("anchor"),
    }
    if include_path:
        result["path"] = chunk.get("path")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Lookup rules in a local user-built DRG board-game lexical index")
    ap.add_argument("query", nargs="+", help="Search query")
    ap.add_argument("--index-dir", type=Path, default=os.environ.get("DRG_INDEX_DIR", ".drg-index"), help="Directory containing manifest.json and chunks.jsonl.")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--source", help="Optional case-insensitive source substring filter")
    ap.add_argument("--include-path", action="store_true", help="Include local filesystem paths in JSON results. Off by default for public-safe output.")
    args = ap.parse_args()

    query = " ".join(args.query).strip()
    terms = query_terms(query)
    chunks, manifest = load_index(args.index_dir.expanduser())
    if args.source:
        needle = args.source.lower()
        chunks = [c for c in chunks if needle in str(c.get("source", "")).lower()]

    ranked = []
    for chunk in chunks:
        s = score_chunk(chunk, terms, manifest)
        if s > 0:
            ranked.append((s, chunk))
    ranked.sort(key=lambda item: (-item[0], str(item[1].get("source", "")), item[1].get("page") or 0, str(item[1].get("heading", ""))))

    results = [make_result(ch, score, args.include_path) for score, ch in ranked[: max(1, args.limit)]]
    print(json.dumps({"query": query, "terms": terms, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
