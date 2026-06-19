#!/usr/bin/env python3
"""Build a private board-game RAG index with semantic + lexical retrieval data."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

PAGE_RE = re.compile(r"^##\s+Page\s+(\d+)\s+\{#([^}]+)\}\s*$", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
WORD_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)
MAX_EXCERPT_CHARS = 420


def slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text.lower()).strip("-")
    return out or "section"


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text) if len(t.strip()) > 1]


def clean_line(line: str) -> str:
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", line)
    line = re.sub(r"\[[^\]]+\]\([^)]*\)", lambda m: re.sub(r"[\[\]()]+", " ", m.group(0)), line)
    line = re.sub(r"`+", "", line)
    return re.sub(r"\s+", " ", line).strip()


def make_excerpt(text: str) -> str:
    lines = [clean_line(x) for x in text.splitlines()]
    lines = [x for x in lines if x and not x.startswith("---")]
    excerpt = re.sub(r"\s+", " ", " ".join(lines)).strip()
    if len(excerpt) <= MAX_EXCERPT_CHARS:
        return excerpt
    cut = excerpt[:MAX_EXCERPT_CHARS].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def display_source(path: Path) -> str:
    return path.stem.replace(" - cleaned", "").replace("_", " ")


def chunk_page(page_lines: List[str], path: Path, page: Optional[int], page_anchor: Optional[str], doc_title: str) -> Iterable[Dict]:
    sections: List[Dict] = []
    current_heading = f"Page {page}" if page else doc_title
    current_anchor = page_anchor or slug(doc_title)
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_lines
        text = "\n".join(current_lines).strip()
        if text:
            sections.append({"heading": current_heading, "anchor": current_anchor, "text": text})
        current_lines = []

    for line in page_lines:
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) >= 3:
            flush()
            title = re.sub(r"\s+\{#[^}]+\}\s*$", "", hm.group(2)).strip()
            current_heading = title or (f"Page {page}" if page else doc_title)
            current_anchor = f"{page_anchor}-{slug(title)}" if page_anchor else slug(title)
        elif not line.strip():
            flush()
        else:
            current_lines.append(line)
    flush()

    if not sections:
        sections = [{"heading": current_heading, "anchor": current_anchor, "text": "\n".join(page_lines).strip()}]

    for idx, sec in enumerate(sections):
        excerpt = make_excerpt(sec["text"])
        terms = tokenize(sec["heading"] + " " + excerpt)
        if not terms or not excerpt:
            continue
        stable = f"{path.name}|{page or ''}|{sec['anchor']}|{idx}"
        yield {
            "id": hashlib.sha1(stable.encode("utf-8")).hexdigest()[:16],
            "source": display_source(path),
            "page": page,
            "heading": sec["heading"],
            "anchor": sec["anchor"],
            "excerpt": excerpt,
            "embedding_text": f"{display_source(path)}. Page {page or 'unknown'}. {sec['heading']}. {excerpt}",
            "term_freq": dict(Counter(terms)),
            "length": len(terms),
        }


def parse_markdown(path: Path) -> List[Dict]:
    raw = path.read_text(encoding="utf-8")
    title = path.stem
    chunks: List[Dict] = []
    current_page: Optional[int] = None
    current_anchor: Optional[str] = None
    page_lines: List[str] = []
    preface: List[str] = []

    def flush_page() -> None:
        nonlocal page_lines
        chunks.extend(chunk_page(page_lines, path, current_page, current_anchor, title))
        page_lines = []

    for line in raw.splitlines():
        m = PAGE_RE.match(line)
        if m:
            if current_page is not None:
                flush_page()
            preface = []
            current_page = int(m.group(1))
            current_anchor = m.group(2)
            page_lines = []
            continue
        if current_page is None:
            preface.append(line)
        else:
            page_lines.append(line)
    if current_page is None:
        chunks.extend(chunk_page(preface, path, None, None, title))
    else:
        flush_page()
    return chunks


def write_semantic_index(chunks: List[Dict], output_dir: Path, model_name: str) -> Dict:
    try:
        import numpy as np  # noqa: F401
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:
        return {"available": False, "error": f"semantic dependencies unavailable: {e}"}
    import numpy as np  # type: ignore

    model = SentenceTransformer(model_name)
    embeddings = model.encode([c["embedding_text"] for c in chunks], normalize_embeddings=True, show_progress_bar=True)
    np.save(output_dir / "embeddings.npy", embeddings)
    return {"available": True, "model": model_name, "path": "embeddings.npy", "dimensions": int(embeddings.shape[1])}


def write_lexical_index(chunks: List[Dict], output_dir: Path) -> Dict:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    except Exception as e:
        return {"available": False, "error": f"sklearn unavailable: {e}"}
    texts = [f"{c['source']} {c['heading']} {c['excerpt']}" for c in chunks]
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    with (output_dir / "vectorizer.pkl").open("wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix}, f)
    return {"available": True, "path": "vectorizer.pkl", "features": len(vectorizer.vocabulary_)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build board-game semantic RAG index")
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--doc", action="append", required=True, help="Markdown filename under --source-dir; repeatable")
    ap.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2")
    ap.add_argument("--no-semantic", action="store_true")
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_chunks: List[Dict] = []
    sources = []
    for name in args.doc:
        path = args.source_dir / name
        if not path.exists():
            raise FileNotFoundError(path)
        chunks = parse_markdown(path)
        all_chunks.extend(chunks)
        sources.append({"file": name, "sha256": file_sha256(path), "chunks": len(chunks)})
    if not all_chunks:
        raise SystemExit("No chunks produced; check source markdown/page anchors")

    doc_freq: Counter = Counter()
    for ch in all_chunks:
        doc_freq.update(ch["term_freq"].keys())
    avg_len = sum(ch["length"] for ch in all_chunks) / max(1, len(all_chunks))

    with (args.output_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False, sort_keys=True) + "\n")

    semantic = {"available": False, "error": "disabled with --no-semantic"} if args.no_semantic else write_semantic_index(all_chunks, args.output_dir, args.embedding_model)
    lexical = write_lexical_index(all_chunks, args.output_dir)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "index_version": 1,
        "chunk_count": len(all_chunks),
        "avg_chunk_length": avg_len,
        "doc_freq": dict(sorted(doc_freq.items())),
        "sources": sources,
        "chunks_path": "chunks.jsonl",
        "semantic": semantic,
        "lexical": lexical,
        "notes": "Private board-game RAG index. chunks.jsonl stores short excerpts only; source material remains private.",
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"chunks": len(all_chunks), "output_dir": str(args.output_dir), "semantic": semantic, "lexical": lexical}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
