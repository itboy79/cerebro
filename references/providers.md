# Providers & Harnesses — running Cerebro anywhere

Cerebro is a **protocol**, not a product: markdown in, markdown out, plus
ordinary file reads/writes. Anything that can do those three things can
run the protocol. This file collects per-harness notes and the delegation
pattern for huge repos.

## Harness notes

| Harness | Notes |
|---------|-------|
| Claude Code | Native. Install as a skill; `/cerebro` triggers directly. Subagents may parallelize scan chunks (see Delegation). |
| Cursor / Windsurf | Add SKILL.md (or its body) to project rules / `.cursorrules`-equivalent, or paste on demand. File tools cover the whole protocol. |
| Aider | `/read SKILL.md` then instruct "run /cerebro scan". Aider's git awareness makes SYNC trivial. |
| Raw API (any vendor) | Drive with a thin loop: send SKILL.md as system prompt, expose read/write/list file tools. Works with Anthropic, OpenAI-compatible endpoints (Azure, Groq, Together…), Gemini, Mistral. |
| Ollama / local models | Same as raw API against `http://localhost:11434/v1`. Prefer ≥32k context models for SCAN; SYNC and RECALL run fine on smaller windows because they load few pages. |
| No harness at all | A human can execute the protocol by hand. Slowly. It still works — that's the point. |

## Capability floor

- **Required:** read files, write files, list directories.
- **Nice to have:** shell (for the two helper scripts and git), git
  (commit anchors for state), Python 3 (helpers).
- **Absent shell/git/Python:** everything degrades to manual protocol +
  fingerprint mode, as described in SKILL.md's failure doctrine.

## Delegation pattern (huge repos, mixed fleets)

For repos too large for one context window, the cortex (the session's
strongest model) may delegate per-module scan chunks to cheaper or local
models — Brigade-style:

1. The cortex runs the scan script, splits the tree into module-sized chunks.
2. Each delegate model receives: the writing rules from
   `references/wiki-model.md` (verbatim), one chunk's file list, and the
   instruction to return **draft page bodies only** — never to write files.
3. The cortex reviews every draft against the actual files before
   writing a single page (fresh-palate rule: never trust a delegate's
   self-report).
4. Only the cortex writes the wiki and seals `state.json`.

Interop: if the repo already has a `.brigade/config.json`, its `cook`
provider/model is a sensible default delegate. Cerebro never requires
Brigade — it only borrows its cooks when they happen to be in the kitchen.
