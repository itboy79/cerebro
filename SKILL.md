---
name: cerebro
description: Repo-wide knowledge engine — scans the entire repository (or project folder) and writes a Karpathy-style wiki-OS, numbered LLM-first markdown pages that become the project's single source of truth, then keeps it in sync forever. Use this skill whenever the user invokes /cerebro, asks to "scan the repo", "map the codebase", "read the whole project", create/update/sync a "wiki", "wiki-OS", "knowledge base" or "docs for LLMs", mentions "source of truth", "drift", onboarding an AI onto an unfamiliar codebase, or starts non-trivial development in a repo that has (or should have) a wiki/ directory. Model-agnostic — works with any LLM that can read and write files; no vendor tools, no APIs, no dependencies required.
---

# CEREBRO

*Every file is a neuron. The wiki is the connectome.*

A brain for your repository: it reads every neuron, follows every axon,
and writes what it learns into one place — the **wiki-OS**, numbered
markdown pages written for models, readable by humans, treated as the
single source of truth for all development that follows.

Glossary (neural → engineering): scan = full repo read · neuron = source
file · connectome = the wiki-OS · impulse = change since last sync ·
drift = wiki/code divergence · the cortex = the model running this skill (you).

```
USAGE:   /cerebro                → scan (first time) or sync (thereafter)
         /cerebro scan          → force a full scan → (re)generate the wiki
         /cerebro sync          → update the wiki from impulses (changes) since last sync
         /cerebro recall <q>    → answer/develop using the wiki as truth
         /cerebro audit         → hunt drift: wiki claims vs actual code
```

## The Three Laws (non-negotiable)

1. **The wiki is the source of truth.** When developing in a Cerebro-enabled
   repo, read the relevant wiki pages *before* reading code, and trust them
   for intent, conventions and invariants. Code tells you what *is*; the
   wiki tells you what *should be*.
2. **No task ends without a sync.** Any change to the repo ends with the
   affected wiki pages updated in the same commit. Code merged without its
   wiki update is an unfinished task.
3. **Drift must be declared, never silently fixed.** If code and wiki
   disagree, surface it to the user with both versions and ask which one is
   truth. Never quietly rewrite the wiki to match code (or vice versa).

## Step 0 — First spark (intro)

Run the intro animation once per session:

```bash
python3 scripts/cerebro_intro.py
```

Neural pulses ripple outward, neurons fire, `CEREBRO ONLINE` (~4s, pure ANSI, zero
dependencies; prints a single static frame when stdout is not a TTY). Never
let it block or crash the run — on any error, skip silently and continue.

## Step 1 — Load configuration

Look for `.cerebro/config.json` in the repo root. If absent, copy
`assets/config.example.json` there and tell the user they can edit it.

```json
{
  "wiki_dir": "wiki",
  "language": "en",
  "pages": "auto",
  "ignore": ["node_modules", ".git", "dist", "build", "target", ".next", "vendor", "__pycache__"],
  "max_file_kb": 256,
  "laws": { "source_of_truth": true, "sync_every_task": true, "declare_drift": true }
}
```

State lives in `.cerebro/state.json` (written by Cerebro, never by hand):
`last_sync_commit`, `last_sync_time`, and the page map.

**Mode resolution:** no `wiki_dir` → SCAN. Wiki + state present → SYNC.
Explicit subcommand always wins.

## Step 2 — SCAN (read every neuron)

1. **Map before reading.** If Python 3 is available, run
   `python3 scripts/cerebro_scan.py <repo-root>` — it prints a deterministic
   repo map (tree, language stats, entry points, largest files, git info)
   so you don't burn context walking directories. No Python? Build the same
   map with the tools you have (`ls -R`, file reads); the protocol is
   identical.
2. **Read in priority order:** manifests and lockfile names first
   (`package.json`, `Cargo.toml`, `pyproject.toml`, …), then entry points,
   then config/CI, then source by module, then tests. Respect `ignore` and
   `max_file_kb` — for oversized or generated files, record their existence
   and role, don't ingest them.
3. **Write the wiki** into `wiki_dir`, following the page catalogue and
   LLM-first writing rules in `references/wiki-model.md` — read that file
   before writing your first page. Core rules, in brief: numbered stable
   pages, index-first, dense and factual, every claim cites a real path,
   explicit invariants and DO-NOT lists, no marketing, no hollow pages
   (skip pages the repo gives you nothing for).
4. **Seal the state:** write `.cerebro/state.json` with the current commit
   (or a content fingerprint when git is absent), then commit the wiki.

Show the user the index (page list + one-liners) when the scan completes.

## Step 3 — SYNC (follow the impulses)

1. Read `.cerebro/state.json`. With git: `git diff --stat <last_sync_commit>..HEAD`
   (plus uncommitted changes) is your impulse list. Without git: compare
   fingerprints from the scan script.
2. Map each changed file to its wiki pages via the page map; update **only**
   those pages. New modules or concepts get new pages, registered in
   `00-INDEX.md`.
3. Append one line per sync to the changelog page: date, commit range,
   pages touched, one-sentence summary.
4. Re-seal `state.json`. Commit wiki updates together with (or immediately
   after) the code they describe — Law 2.

## Step 4 — RECALL (the wiki drives development)

When the user develops anything in a Cerebro-enabled repo:

1. Open `00-INDEX.md`, load only the pages relevant to the task.
2. Follow the wiki's conventions, invariants and decisions as binding.
3. If the task forces you to contradict a wiki page → that's drift → Law 3:
   stop, show both versions, let the user pick the truth.
4. End the task with Step 3 (sync). Always.

## Step 5 — AUDIT (drift hunt)

On `/cerebro audit`: sample the strongest claims from each wiki page
(paths, commands, invariants) and verify them against the actual repo —
files exist, commands are real, described flows match code. Report:

```
🧠 CEREBRO — audit complete.

INTACT    <pages fully verified>
DRIFT     <page · claim · what the code actually says>
UNKNOWN   <claims that could not be verified and why>
```

Then apply Law 3 to every drift found.

## Summary block

End every scan/sync with this exact structure:

```
🧠 CEREBRO — the map is the territory. Cortex at rest.

SCAN      <files read · files skipped and why>
PAGES     <pages written/updated, one line each>
STATE     <commit sealed in state.json>
NEXT      <suggested next step, if any>
```

## Model-agnostic doctrine

- The entire protocol is **plain markdown + file reads/writes**. Any model
  in any harness (Claude Code, Cursor, Windsurf, Aider, raw API, local
  Ollama) can run it. See `references/providers.md` for per-harness notes
  and for delegating scan chunks to cheaper/local models on huge repos.
- The two Python helpers are conveniences, not requirements — everything
  degrades gracefully to manual protocol.
- Never assume a vendor tool exists. Probe, then adapt.

## Failure doctrine

- Unreadable or binary file → record path + role in the wiki, move on.
- Repo too large for one pass → scan by top-level module, one wiki page per
  pass, and say so in the summary; never pretend a partial scan was full.
- Missing git → fingerprint mode (the scan script computes it); syncs still
  work, only the commit anchors are absent.
- A corrupted or hand-edited `state.json` → warn, offer a fresh `/cerebro scan`.
- Document everything: a stranger (human or model) must be able to rebuild
  your reasoning from the wiki and the summary alone.
