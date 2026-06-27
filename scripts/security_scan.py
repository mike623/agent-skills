#!/usr/bin/env python3
"""Public-safety scanner for the agent-skills repository.

This repo is intended to be public and reusable. The scanner blocks common
credential patterns plus repo-specific leaks such as private absolute paths,
Hermes profile/secure paths, generated state, and non-example env files.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".omc",
    ".claude",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

TEXT_SUFFIXES = {
    "",
    ".bash",
    ".cfg",
    ".conf",
    ".css",
    ".csv",
    ".env",
    ".example",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".lock",
    ".md",
    ".py",
    ".rb",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}

ALLOWLIST_PATH_FRAGMENTS = {
    "scripts/security_scan.py",
    ".github/workflows/security.yml",
    ".pre-commit-config.yaml",
}

# Exact strings/patterns that are safe because they document the policy itself.
ALLOWLIST_LINE_PATTERNS = [
    re.compile(r"Never commit secrets"),
    re.compile(r"no private filesystem paths", re.I),
    re.compile(r"Do not commit private absolute workspace paths"),
    re.compile(r"Private local runtime scripts may live"),
    re.compile(r"Runtime scripts with private local paths/state"),
    re.compile(r"/Users/<name>"),
    re.compile(r"/home/<name>"),
    re.compile(r"<workspace-root>"),
    re.compile(r"<career-ops-workspace>"),
    re.compile(r"<user-home-or-vault-workdir>"),
    re.compile(r"<vault-or-output-dir>"),
    re.compile(r"<path-to-existing-app>"),
    re.compile(r"<bookmark_id>"),
    re.compile(r"<github-org/repo>"),
    re.compile(r"gh[pousr]_\[A-Za-z0-9_\]"),
    re.compile(r"AKIA\[0-9A-Z\]"),
    re.compile(r"AIza\[0-9A-Za-z_\-\]"),
    re.compile(r"Bearer\\s\+"),
    re.compile(r"-----BEGIN .*PRIVATE KEY-----"),
]


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    severity: str = "error"


RULES = [
    Rule("private-key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
    Rule("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    Rule("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    Rule("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
    Rule("google-api-key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    Rule("bearer-token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{24,}")),
    Rule("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    Rule("private-macos-path", re.compile(r"/Users/(?!<name>)(?![^\s`'\"]*<)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._ @+,-]+)+")),
    Rule("private-linux-home-path", re.compile(r"/home/(?!<name>)(?![^\s`'\"]*<)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._ @+,-]+)+")),
    Rule("hermes-profile-path", re.compile(r"(?:~|/[^\s`'\"]+)/\.hermes/profiles/[^\s`'\"]+")),
    Rule("hermes-secure-path", re.compile(r"(?:~|/[^\s`'\"]+)/\.hermes/secure/[^\s`'\"]*")),
    Rule("cookie-store-reference", re.compile(r"\b(Cookies|Cookie\.binarycookies|cookie_inventory|RefreshToken|Jwt)\b")),
]

SUSPICIOUS_FILENAMES = [
    re.compile(r"(^|/)\.env($|\.)"),
    re.compile(r"\.pem$"),
    re.compile(r"\.p12$"),
    re.compile(r"\.p8$"),
    re.compile(r"\.mobileprovision$"),
    re.compile(r"cookie", re.I),
    re.compile(r"state\.json$", re.I),
]

ALLOWED_FILENAMES = {
    "skills/flutter-release-flow/templates/.env.example",
    "skills/raindrop-bookmark-curator/templates/raindrop-state.example.json",
    "skills/raindrop-bookmark-curator/templates/collection-taxonomy.example.json",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    snippet: str


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def iter_files(paths: Iterable[str] | None) -> Iterable[Path]:
    if paths:
        for raw in paths:
            p = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
            if p.is_file() and ROOT in p.parents:
                yield p
            elif p.is_dir() and ROOT in p.parents:
                yield from walk(p)
        return
    yield from walk(ROOT)


def walk(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.is_file():
            yield p


def is_text_candidate(path: Path) -> bool:
    if path.suffix in TEXT_SUFFIXES:
        return True
    name = path.name
    return name in {"README", "LICENSE", "Dockerfile", "Fastfile"}


def is_allowlisted_line(line: str) -> bool:
    return any(p.search(line) for p in ALLOWLIST_LINE_PATTERNS)


def mask(snippet: str) -> str:
    snippet = re.sub(r"[A-Za-z0-9._~+/=-]{12,}", lambda m: m.group(0)[:4] + "…" + m.group(0)[-4:], snippet)
    return snippet.strip()[:180]


def check_filename(path: Path) -> list[Finding]:
    r = rel(path)
    if r in ALLOWED_FILENAMES:
        return []
    findings: list[Finding] = []
    for pat in SUSPICIOUS_FILENAMES:
        if pat.search(r):
            findings.append(Finding(path, 0, "suspicious-filename", r))
            break
    return findings


def check_content(path: Path) -> list[Finding]:
    r = rel(path)
    if any(fragment == r for fragment in ALLOWLIST_PATH_FRAGMENTS):
        # The scanner and hook config necessarily contain the patterns they enforce.
        return []
    if not is_text_candidate(path):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_allowlisted_line(line):
            continue
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(Finding(path, lineno, rule.name, mask(line)))
    return findings


def staged_files() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan public agent skills for secrets/private local leakage.")
    parser.add_argument("paths", nargs="*", help="Optional files/directories to scan. Defaults to the repo.")
    parser.add_argument("--staged", action="store_true", help="Scan staged files only, for pre-commit.")
    args = parser.parse_args()

    paths = staged_files() if args.staged else args.paths
    findings: list[Finding] = []
    for path in iter_files(paths):
        findings.extend(check_filename(path))
        findings.extend(check_content(path))

    if findings:
        print("Public-safety scan failed:\n")
        for f in findings:
            location = f"{rel(f.path)}" + (f":{f.line}" if f.line else "")
            print(f"- [{f.rule}] {location}\n  {f.snippet}")
        print("\nFix by replacing private values with placeholders or moving private runtime/state files out of this public repo.")
        return 1

    target = "staged files" if args.staged else "repo"
    print(f"Public-safety scan passed for {target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
