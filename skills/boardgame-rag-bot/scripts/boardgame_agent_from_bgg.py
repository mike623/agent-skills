#!/usr/bin/env python3
"""Bootstrap a private board-game rules agent package from a BGG link plus a user-provided PDF.

This script intentionally does not bypass BGG auth or scrape private files. It fetches
public BGG XML metadata, copies/downloads a rulebook supplied by the user, extracts a
basic page-anchored Markdown file, builds a local RAG index, and writes a generated
agent skill.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BGG_RE = re.compile(r"boardgamegeek\.com/(?:boardgame|thing)/(\d+)(?:/([^/?#]+))?")


def slugify(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return out or "boardgame"


def parse_bgg_url(url: str) -> tuple[str, str | None]:
    m = BGG_RE.search(url)
    if not m:
        raise SystemExit(f"Could not parse BGG boardgame id from URL: {url}")
    return m.group(1), m.group(2)


def fetch_bgg_metadata(bgg_id: str, bgg_url: str) -> dict:
    api = f"https://boardgamegeek.com/xmlapi2/thing?id={urllib.parse.quote(bgg_id)}&stats=1"
    with urllib.request.urlopen(api, timeout=30) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    item = root.find("item")
    if item is None:
        raise SystemExit(f"BGG returned no item for id {bgg_id}")
    names = item.findall("name")
    primary = next((n for n in names if n.attrib.get("type") == "primary"), names[0] if names else None)
    title = primary.attrib.get("value") if primary is not None else None
    if not title:
        title = f"BoardGame {bgg_id}"
    year_el = item.find("yearpublished")

    def values(link_type: str) -> list[str]:
        return [x.attrib.get("value", "") for x in item.findall("link") if x.attrib.get("type") == link_type and x.attrib.get("value")]

    metadata = {
        "bgg_id": bgg_id,
        "bgg_url": bgg_url,
        "title": title,
        "slug": slugify(title),
        "year": year_el.attrib.get("value") if year_el is not None else None,
        "description": (item.findtext("description") or "").strip(),
        "designers": values("boardgamedesigner"),
        "publishers": values("boardgamepublisher"),
        "categories": values("boardgamecategory"),
        "mechanics": values("boardgamemechanic"),
    }
    return metadata


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "boardgame-rag-bot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


def extract_pdf_to_markdown(pdf: Path, md: Path, raw: Path) -> None:
    text = ""
    try:
        import fitz  # type: ignore
        doc = fitz.open(str(pdf))
        parts = []
        raw_parts = []
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            raw_parts.append(page_text)
            parts.append(f"## Page {i} {{#page-{i}}}\n\n{page_text.strip()}\n")
        text = "\n".join(parts)
        raw.write_text("\n\n".join(raw_parts), encoding="utf-8")
    except Exception:
        # Fallback to pdftotext if installed.
        proc = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], text=True, capture_output=True, check=True)
        raw.write_text(proc.stdout, encoding="utf-8")
        pages = proc.stdout.split("\f")
        text = "\n".join(f"## Page {i} {{#page-{i}}}\n\n{p.strip()}\n" for i, p in enumerate(pages, start=1) if p.strip())
    md.write_text(text, encoding="utf-8")


def render_template(template_path: Path, replacements: dict[str, str]) -> str:
    text = template_path.read_text(encoding="utf-8")
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a private board-game RAG agent package from BGG metadata + rulebook PDF")
    ap.add_argument("bgg_url")
    ap.add_argument("--pdf", type=Path, help="Local rulebook PDF to copy into the private package")
    ap.add_argument("--pdf-url", help="Direct public rulebook PDF URL to download")
    ap.add_argument("--out", type=Path, required=True, help="Private output package directory")
    ap.add_argument("--no-semantic", action="store_true", help="Skip semantic embeddings during index build")
    args = ap.parse_args()

    if not args.pdf and not args.pdf_url:
        raise SystemExit("Provide --pdf or --pdf-url. BGG file discovery is best-effort and not implemented in this MVP.")

    bgg_id, url_slug = parse_bgg_url(args.bgg_url)
    metadata = fetch_bgg_metadata(bgg_id, args.bgg_url)
    game_slug = url_slug or metadata["slug"]

    out = args.out.expanduser().resolve()
    sources = out / "sources"
    rag = out / "rag"
    scripts = out / "scripts"
    for d in (sources, rag, scripts):
        d.mkdir(parents=True, exist_ok=True)

    (sources / "bgg-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (sources / "source-links.json").write_text(json.dumps({"bgg_url": args.bgg_url, "pdf_url": args.pdf_url}, indent=2) + "\n", encoding="utf-8")

    pdf_dest = sources / "rulebook.pdf"
    if args.pdf_url:
        download(args.pdf_url, pdf_dest)
    else:
        shutil.copy2(args.pdf.expanduser(), pdf_dest)

    extract_pdf_to_markdown(pdf_dest, sources / "rulebook.md", sources / "rulebook.raw.txt")

    skill_dir = Path(__file__).resolve().parents[1]
    shutil.copy2(skill_dir / "scripts" / "lookup_boardgame_rag.py", scripts / "lookup.py")
    shutil.copy2(skill_dir / "scripts" / "build_boardgame_rag.py", scripts / "build_rag.py")
    (scripts / "lookup.py").chmod(0o755)
    (scripts / "build_rag.py").chmod(0o755)

    build_cmd = [sys.executable, str(scripts / "build_rag.py"), "--source-dir", str(sources), "--output-dir", str(rag), "--doc", "rulebook.md"]
    if args.no_semantic:
        build_cmd.append("--no-semantic")
    subprocess.run(build_cmd, check=True)

    replacements = {
        "<game-slug>": game_slug,
        "<Game Title>": metadata["title"],
        "<sources-dir>": str(sources),
        "<rag-dir>": str(rag),
        "<lookup-script>": str(scripts / "lookup.py"),
        "<BGG URL>": args.bgg_url,
    }
    (out / "SKILL.md").write_text(render_template(skill_dir / "templates" / "game-skill.md", replacements), encoding="utf-8")
    (out / "README.md").write_text(render_template(skill_dir / "templates" / "agent-readme.md", replacements), encoding="utf-8")

    print(json.dumps({
        "title": metadata["title"],
        "bgg_id": bgg_id,
        "out": str(out),
        "lookup": str(scripts / "lookup.py"),
        "test": f"{scripts / 'lookup.py'} --index-dir {rag} setup --limit 5",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
