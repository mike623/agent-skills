#!/usr/bin/env python3
"""Build a local, public-safe lexical index for Deep Rock Galactic board-game notes.

The script indexes user-supplied Markdown/text files and stores short excerpts plus
term statistics. It intentionally ships with no copyrighted rule text, no private
paths, no tokens, and no generated index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

PAGE_RE = re.compile(r"^#{1,6}\s+Page\s+(\d+)\s*(?:\{#([^}]+)\})?\s*$", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
WORD_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)
MAX_EXCERPT_CHARS = 360
DEFAULT_GLOBS = ["*.md", "*.markdown", "*.txt"]


def slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text.lower()).strip("-")
    return out or "section"


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text) if len(t.strip()) > 1]


def clean_line(line: str) -> str:
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", line)
    line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"`+", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def make_excerpt(text: str, max_chars: int = MAX_EXCERPT_CHARS) -> str:
    lines = [clean_line(x) for x in text.splitlines()]
    lines = [x for x in lines if x and not x.startswith("---")]
    excerpt = re.sub(r"\s+", " ", " ".join(lines)).strip()
    if len(excerpt) <= max_chars:
        return excerpt
    cut = excerpt[:max_chars].rsplit(" ", 1)[0] or excerpt[:max_chars]
    return cut.rstrip(".,;:") + "…"


def display_source(path: Path, source_dir: Path) -> str:
    try:
        rel = path.relative_to(source_dir)
        return str(rel.with_suffix(""))
    except ValueError:
        return path.stem


def chunk_page(page_lines: List[str], path: Path, source_dir: Path, page: Optional[int], page_anchor: Optional[str], doc_title: str, max_excerpt_chars: int) -> Iterable[Dict]:
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

    fallback = {"heading": current_heading, "anchor": current_anchor, "text": "\n".join(page_lines).strip()}
    for idx, sec in enumerate(sections or [fallback]):
        text = sec["text"]
        terms = tokenize(sec["heading"] + " " + text)
        if not terms:
            continue
        stable = f"{path.name}|{page or ''}|{sec['anchor']}|{idx}"
        yield {
            "id": hashlib.sha1(stable.encode("utf-8")).hexdigest()[:16],
            "source": display_source(path, source_dir),
            "page": page,
            "heading": sec["heading"],
            "path": str(path),
            "anchor": sec["anchor"],
            "excerpt": make_excerpt(text, max_excerpt_chars),
            "term_freq": dict(Counter(terms)),
            "length": len(terms),
        }


def parse_document(path: Path, source_dir: Path, max_excerpt_chars: int) -> List[Dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    title = path.stem
    chunks: List[Dict] = []
    current_page: Optional[int] = None
    current_anchor: Optional[str] = None
    page_lines: List[str] = []
    preface: List[str] = []

    def flush_page() -> None:
        nonlocal page_lines
        chunks.extend(chunk_page(page_lines, path, source_dir, current_page, current_anchor, title, max_excerpt_chars))
        page_lines = []

    for line in raw.splitlines():
        m = PAGE_RE.match(line)
        if m:
            if current_page is not None:
                flush_page()
            preface = []
            current_page = int(m.group(1))
            current_anchor = m.group(2) or f"page-{current_page}"
            page_lines = []
            continue
        if current_page is None:
            preface.append(line)
        else:
            page_lines.append(line)
    if current_page is None:
        chunks.extend(chunk_page(preface, path, source_dir, None, None, title, max_excerpt_chars))
    else:
        flush_page()
    return chunks


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_sources_config(path: Optional[Path]) -> Dict:
    if not path:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def discover_docs(source_dir: Path, docs: Optional[Sequence[str]], globs: Sequence[str]) -> List[Path]:
    if docs:
        return [(source_dir / name).expanduser() for name in docs]
    found: List[Path] = []
    for pattern in globs:
        found.extend(p for p in source_dir.glob(pattern) if p.is_file())
    return sorted(set(found))


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a local lexical index for user-provided DRG board-game docs")
    ap.add_argument("--source-dir", type=Path, default=os.environ.get("DRG_SOURCE_DIR"), help="Directory containing local Markdown/text docs (or DRG_SOURCE_DIR).")
    ap.add_argument("--index-dir", "--output-dir", dest="index_dir", type=Path, default=os.environ.get("DRG_INDEX_DIR", ".drg-index"), help="Directory for generated chunks.jsonl and manifest.json.")
    ap.add_argument("--sources-config", type=Path, help="Optional JSON config with source_dir, index_dir, docs, globs, and max_excerpt_chars.")
    ap.add_argument("--doc", action="append", help="Filename/path relative to source-dir to index; repeatable. Defaults to matching Markdown/text files.")
    ap.add_argument("--glob", action="append", help="Glob to discover files when --doc is not supplied. Defaults to *.md, *.markdown, *.txt.")
    ap.add_argument("--max-excerpt-chars", type=int, default=MAX_EXCERPT_CHARS, help="Maximum stored excerpt length per chunk.")
    args = ap.parse_args()

    cfg = load_sources_config(args.sources_config)
    source_dir_value = args.source_dir or cfg.get("source_dir")
    if not source_dir_value:
        raise SystemExit("Provide --source-dir, DRG_SOURCE_DIR, or sources_config.source_dir. No private default is embedded.")
    source_dir = Path(source_dir_value).expanduser()
    index_dir = Path(cfg.get("index_dir") or args.index_dir).expanduser()
    docs = args.doc or cfg.get("docs")
    globs = args.glob or cfg.get("globs") or DEFAULT_GLOBS
    max_excerpt_chars = int(cfg.get("max_excerpt_chars") or args.max_excerpt_chars)

    if not source_dir.exists():
        raise FileNotFoundError(source_dir)
    paths = discover_docs(source_dir, docs, globs)
    if not paths:
        raise SystemExit(f"No source documents found in {source_dir}")

    index_dir.mkdir(parents=True, exist_ok=True)
    all_chunks: List[Dict] = []
    manifest_sources = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        chunks = parse_document(path, source_dir, max_excerpt_chars)
        all_chunks.extend(chunks)
        manifest_sources.append({"path": str(path), "sha256": file_sha256(path), "chunks": len(chunks)})

    doc_freq: Counter = Counter()
    for ch in all_chunks:
        doc_freq.update(ch["term_freq"].keys())
    avg_len = sum(ch["length"] for ch in all_chunks) / max(1, len(all_chunks))

    chunks_path = index_dir / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False, sort_keys=True) + "\n")

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "index_version": 1,
        "chunk_count": len(all_chunks),
        "avg_chunk_length": avg_len,
        "doc_freq": dict(sorted(doc_freq.items())),
        "sources": manifest_sources,
        "chunks_path": str(chunks_path),
        "notes": "Public-safe local lexical index: generated from user-provided docs; stores short excerpts only; no embeddings or bundled rule text.",
    }
    (index_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"chunks": len(all_chunks), "index_dir": str(index_dir), "sources": manifest_sources}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
