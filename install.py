#!/usr/bin/env python3
"""CEREBRO installer — puts the skill where your agent can find it.

Zero dependencies (stdlib only). Works two ways:

  • From a cloned repo:   python3 install.py
  • Standalone one-liner:  curl -sSL <raw>/install.py | python3 -

Targets, in order of the flags below:
  (default)      personal   ~/.claude/skills/cerebro        (all projects)
  --project      project    ./.claude/skills/cerebro        (this repo only)
  --dir PATH     custom     PATH/cerebro
  --agent NAME   swap the base dir for another agent
                 (claude → ~/.claude, openclaw → ~/.openclaw, cursor/codex/gemini
                  → their conventional dirs; anything with a SKILL.md loader works)

It never double-nests, sets the helper scripts executable, and prints how to
verify the install. Re-running upgrades in place.
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO = "itboy79/cerebro"
BRANCH = "main"
TARBALL = f"https://codeload.github.com/{REPO}/tar.gz/refs/heads/{BRANCH}"
SKILL_NAME = "cerebro"
# the parts of the repo that actually make up the skill (README/LICENSE/installer excluded)
SKILL_PARTS = ("SKILL.md", "assets", "references", "scripts")

PURPLE = "\033[38;5;135m"
DIM = "\033[38;5;245m"
GREEN = "\033[38;5;42m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color(s: str, c: str) -> str:
    return s if not sys.stdout.isatty() else f"{c}{s}{RESET}"


AGENT_DIRS = {
    "claude": Path.home() / ".claude" / "skills",
    "openclaw": Path.home() / ".openclaw" / "skills",
    "cursor": Path.home() / ".cursor" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "gemini": Path.home() / ".gemini" / "skills",
}


def resolve_target(args) -> Path:
    if args.dir:
        return Path(args.dir).expanduser().resolve() / SKILL_NAME
    if args.project:
        return Path.cwd() / ".claude" / "skills" / SKILL_NAME
    base = AGENT_DIRS.get(args.agent)
    if base is None:
        sys.exit(color(f"Unknown --agent '{args.agent}'. Known: {', '.join(AGENT_DIRS)}", DIM))
    return base / SKILL_NAME


def find_local_source() -> Path | None:
    """If this script sits inside a checkout, return the skill root next to it."""
    here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    for candidate in (here, here / SKILL_NAME):
        if (candidate / "SKILL.md").is_file():
            return candidate
    return None


def download_source(dest: Path) -> Path:
    print(color(f"↓ fetching {REPO}@{BRANCH} …", DIM))
    try:
        req = urllib.request.Request(TARBALL, headers={"User-Agent": "cerebro-installer"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
    except Exception as exc:  # noqa: BLE001
        sys.exit(color(f"✗ download failed: {exc}\n  Clone the repo and run install.py from inside it.", DIM))
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
        _safe_extract(tar, dest)
    roots = [p for p in dest.iterdir() if p.is_dir()]
    root = roots[0] if roots else dest
    if not (root / "SKILL.md").is_file():
        sys.exit(color("✗ downloaded archive has no SKILL.md at its root.", DIM))
    return root


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    # guard against path traversal (CVE-2007-4559)
    dest = dest.resolve()
    for member in tar.getmembers():
        target = (dest / member.name).resolve()
        if not str(target).startswith(str(dest)):
            sys.exit(color(f"✗ refusing unsafe path in archive: {member.name}", DIM))
    tar.extractall(dest)  # noqa: S202 — validated above


def install(source: Path, target: Path) -> None:
    if target.exists():
        print(color(f"↻ upgrading existing install at {target}", DIM))
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    copied = []
    for part in SKILL_PARTS:
        src = source / part
        if not src.exists():
            continue
        dst = target / part
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied.append(part)
    if "SKILL.md" not in copied:
        sys.exit(color("✗ no SKILL.md found in source — nothing installed.", DIM))
    # make helper scripts executable
    scripts = target / "scripts"
    if scripts.is_dir():
        for f in scripts.glob("*.py"):
            f.chmod(f.stat().st_mode | 0o111)


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="install.py",
        description="Install the CEREBRO skill for Claude Code (or any SKILL.md agent).",
    )
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--project", action="store_true",
                       help="install into ./.claude/skills (this repo only)")
    scope.add_argument("--dir", metavar="PATH",
                       help="install into PATH/cerebro (custom skills dir)")
    ap.add_argument("--agent", default="claude",
                    help="target agent base dir (default: claude)")
    args = ap.parse_args()

    print(color(f"{BOLD}CEREBRO{RESET}", PURPLE), color("— every file, one neuron.", DIM))
    target = resolve_target(args)

    source = find_local_source()
    tmp = None
    if source:
        print(color(f"• source: local checkout ({source})", DIM))
    else:
        tmp = Path(tempfile.mkdtemp(prefix="cerebro-"))
        source = download_source(tmp)

    try:
        install(source, target)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

    print(color("✓ installed", GREEN), color(f"→ {target}", DIM))
    print()
    print(color("verify:", BOLD))
    print(f'  ls "{target}"                 # should list SKILL.md, assets, references, scripts')
    print("  # start a NEW Claude Code session, then:")
    print(color("  /cerebro", PURPLE) + "                        # scan the repo → write the wiki-OS")
    print()
    print(color("note:", DIM),
          color("Claude Code loads skills at session start — restart before first use.", DIM))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
