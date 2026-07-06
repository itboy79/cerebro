#!/usr/bin/env python3
"""cerebro_scan — deterministic repo map for the SCAN protocol.

Prints a markdown map (tree, language stats, entry points, largest files,
git anchors, content fingerprint) so the model reads the territory before
reading files. Stdlib only. Usage:

    python3 cerebro_scan.py [repo-root] [--max-depth N]

Respects .cerebro/config.json "ignore" if present, plus built-in defaults.
"""
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter

DEFAULT_IGNORE = {
    "node_modules", ".git", "dist", "build", "target", ".next", "vendor",
    "__pycache__", ".venv", "venv", ".cache", "coverage", ".idea", ".vscode",
    ".cerebro",
}
ENTRY_HINTS = (
    "main", "index", "app", "server", "cli", "__main__", "mod", "lib",
)
MANIFESTS = (
    "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml",
    "build.gradle", "Gemfile", "composer.json", "requirements.txt",
    "Makefile", "Dockerfile", "docker-compose.yml", "tauri.conf.json",
)


def load_ignore(root: str) -> set:
    ignore = set(DEFAULT_IGNORE)
    cfg = os.path.join(root, ".cerebro", "config.json")
    try:
        with open(cfg, encoding="utf-8") as f:
            ignore.update(json.load(f).get("ignore", []))
    except (OSError, ValueError):
        pass
    return ignore


def git(root: str, *args: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True, text=True, timeout=10, check=False,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0]) if args else os.getcwd()
    max_depth = 4
    if "--max-depth" in sys.argv:
        try:
            max_depth = int(sys.argv[sys.argv.index("--max-depth") + 1])
        except (IndexError, ValueError):
            pass

    ignore = load_ignore(root)
    langs, sizes, tree_lines, manifests, entries = Counter(), [], [], [], []
    fingerprint = hashlib.sha256()
    n_files = n_skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in ignore and not d.startswith("."))
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth <= max_depth and rel != ".":
            tree_lines.append("  " * (depth - 1) + "├── " + os.path.basename(dirpath) + "/")
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            relf = os.path.relpath(path, root)
            try:
                size = os.path.getsize(path)
            except OSError:
                n_skipped += 1
                continue
            n_files += 1
            ext = os.path.splitext(name)[1].lower() or name
            langs[ext] += 1
            sizes.append((size, relf))
            fingerprint.update(f"{relf}:{size}".encode())
            stem = os.path.splitext(name)[0].lower()
            if name in MANIFESTS:
                manifests.append(relf)
            if stem in ENTRY_HINTS and depth <= 2:
                entries.append(relf)
            if depth <= max_depth - 1:
                tree_lines.append("  " * depth + "├── " + name)

    sizes.sort(reverse=True)
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    head = git(root, "rev-parse", "--short", "HEAD")
    remote = git(root, "remote", "get-url", "origin")

    print(f"# CEREBRO SCAN MAP — {os.path.basename(root)}\n")
    print(f"- Root: `{root}`")
    print(f"- Files: {n_files} (skipped: {n_skipped}) · ignore: {sorted(ignore)}")
    print(f"- Git: branch `{branch or 'n/a'}` · HEAD `{head or 'n/a'}` · remote `{remote or 'n/a'}`")
    print(f"- Fingerprint (structure): `{fingerprint.hexdigest()[:16]}`\n")
    print("## Manifests (read these first)\n")
    print("\n".join(f"- `{m}`" for m in manifests) or "- none found")
    print("\n## Likely entry points\n")
    print("\n".join(f"- `{e}`" for e in sorted(set(entries))) or "- none detected")
    print("\n## Languages / extensions\n")
    for ext, n in langs.most_common(15):
        print(f"- `{ext}` × {n}")
    print("\n## Largest files (top 10 — candidates for skip/summarize)\n")
    for size, relf in sizes[:10]:
        print(f"- {size // 1024:>6} KB  `{relf}`")
    print(f"\n## Tree (depth ≤ {max_depth})\n\n```")
    print("\n".join(tree_lines[:400]))
    if len(tree_lines) > 400:
        print(f"… {len(tree_lines) - 400} more lines truncated")
    print("```")


if __name__ == "__main__":
    main()
