# The Wiki-OS Model (Karpathy-style, LLM-first)

The wiki-OS is documentation written **for models first, humans second** —
the pattern Andrej Karpathy sketched when he argued that codebases will
increasingly be read by LLMs, so their docs should be optimized for an LLM
reader: dense, explicit, self-contained, navigable from a single index.

A model that has never seen the repo must be able to load `00-INDEX.md`,
pick 2–3 pages, and work correctly. That is the bar for every page.

## Page catalogue

Numbered, stable, index-first. `pages: "auto"` means: create only the pages
the repo actually feeds — **never create a hollow page**. Numbers never get
reused; retired pages are marked `RETIRED` in the index, not deleted.

```
wiki/
├── 00-INDEX.md          the map of the map — required, always
├── 01-VISION.md         what this project is, for whom, what it is NOT
├── 02-ARCHITECTURE.md   components, boundaries, data flow, diagrams-as-text
├── 03-STACK.md          languages, frameworks, pinned versions, why each
├── 04-CONVENTIONS.md    naming, style, patterns, the DO-NOT list
├── 05-STRUCTURE.md      directory → responsibility map
├── 06-DATA.md           schemas, models, migrations, storage
├── 07-INTERFACES.md     API / CLI / UI surfaces and contracts
├── 08-TESTING.md        how to run, what must pass, coverage philosophy
├── 09-OPERATIONS.md     build, deploy, environments, secrets handling (names, never values)
├── 10-DECISIONS.md      ADR log — every irreversible choice, dated, with rejected alternatives
├── 11-ROADMAP.md        planned work, priorities, explicitly-cut scope
└── 12-CHANGELOG.md      one line per sync: date · commit range · pages touched · summary
```

Repos with special surfaces extend the numbering from 13 up (e.g.
`13-DESIGN-SYSTEM.md`, `14-ORCHESTRATION.md`, `15-COMPLIANCE.md`).

## Writing rules (the LLM-first ten)

1. **Index-first.** `00-INDEX.md` lists every page with a one-line summary
   and a "load this when…" hint. It is the only page a model must always read.
2. **Self-contained pages.** No page requires another to be understood;
   cross-references are links, not dependencies.
3. **Every claim cites a path.** "Auth lives in `src/auth/session.ts`" —
   never "auth is handled in the usual place". Claims without paths are
   opinions; the wiki holds none.
4. **Dense > pretty.** Short declarative sentences, tables, code fences.
   Zero marketing language, zero filler, zero "simply".
5. **Explicit invariants.** Each page ends with an `## Invariants` section:
   things that must stay true, and a `## DO NOT` list of known traps.
6. **Commands are verbatim.** Every runnable command appears exactly as it
   must be typed, in a fenced block, with its working directory.
7. **State the unknowns.** An honest `UNKNOWN: <thing>` beats a plausible
   guess. Models inherit your hallucinations; don't create any.
8. **Stable anchors.** Page numbers and heading names are API — renaming a
   heading is a breaking change and must be noted in the changelog.
9. **Decisions are append-only.** `10-DECISIONS.md` never edits history;
   a reversed decision gets a new dated entry pointing at the old one.
10. **Written for a cold start.** Assume the reader has zero conversation
    context, zero repo familiarity, and a limited context window.

## Page template

```markdown
# NN — TITLE

> Load this when: <one line — the retrieval hint>
> Last sync: <date> · <commit-short-sha>

<dense body: tables, paths, fenced commands>

## Invariants
- <thing that must remain true, with the path that enforces it>

## DO NOT
- <known trap · why · what to do instead>
```

## Index template

```markdown
# 00 — INDEX

> The map of <repo-name>. Read this first, always. Load only what the task needs.
> Wiki-OS maintained by Cerebro · last sync: <date> · <commit-short-sha>

| Page | Title | Load this when… |
|------|-------|-----------------|
| 01 | Vision | you need intent, scope, audience |
| 02 | Architecture | you touch more than one module |
| …  | …     | … |

## Laws of this repo
1. This wiki is the source of truth (Cerebro Law 1).
2. No task ends without a sync (Cerebro Law 2).
3. Drift is declared, never silently fixed (Cerebro Law 3).
```

## Sizing guidance

- A page over ~300 lines is two pages. Split by responsibility, register
  both in the index.
- The whole wiki should be loadable by a mid-size context model; if the
  repo is huge, prefer more, smaller, better-indexed pages over few
  encyclopedic ones.
