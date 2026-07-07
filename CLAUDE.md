# Jabodetabek Transport

> Peta 3D interaktif transportasi umum Jabodetabek (KRL, MRT, LRT, TransJakarta) dengan simulasi posisi kendaraan real-time berbasis jadwal, dibangun dengan Vite + MapLibre GL + deck.gl.

- Type: `gis-app`
- Scaffolded: 2026-07-07 from Claude Engineering OS
- OS_ROOT: `C:\Users\Luthfi\Documents\Claude Code\Claude Engineering OS`

This project is governed by **Claude Engineering OS**. Consult OS standards on
demand by reading specific files under `OS_ROOT` — do **not** copy their
content into this file.

## Standards in force

Read the relevant one before starting that kind of work (paths relative to
`OS_ROOT`):

- `standards/coding/typescript.md` — TS style for the frontend (see `docs/RULES.md`: this project deviates — vanilla JS, not TS)
- `standards/coding/python.md` — Python style for ETL tools
- `standards/coding/naming-conventions.md` — naming across DB/JS/API
- `standards/design/web-design.md` — design system rules
- `standards/testing.md` — spatial tests use real coordinates
- `knowledge/gis.md` — PostGIS, MapLibre, deck.gl, CRS gotchas

Project-local deviations from OS standards live in `docs/RULES.md` **only** —
this file stays a pointer, never a rulebook.

## Session protocol

**START**
1. Read `docs/memory/STATE.md` (where we are).
2. Read `docs/TASK.md` (what is next).

**WORK** — follow the loop in `OS_ROOT\standards\engineering-principles.md`:
- Plan → Implement → Test → Review → Commit, one small step at a time.
- No coding before the work exists as a `docs/TASK.md` entry.
- Architectural change requires an ADR first (use `/new-adr`).
- The moment a shortcut is taken, record it in `docs/memory/DEBT.md`.

**CLOSE**
1. Run `/project-status` (updates STATE.md, prompts for DEBT/LESSONS entries).
2. Commit with a conventional message per `OS_ROOT\standards\git-workflow.md`.

## Language

- Converse with the user in **Bahasa Indonesia**.
- Code, commits, identifiers: **English**.
- Project docs fill language: **Bahasa Indonesia** (structure stays English).

## Documentation map

| Doc | Answers | Update when |
|---|---|---|
| `README.md` | Front door: what + how to run | quickstart changes |
| `docs/PROJECT_BRIEF.md` | Why this exists — problem, scope, success criteria | scope changes |
| `docs/PRD.md` | Features and acceptance criteria | features change |
| `docs/USER_STORIES.md` | Who needs what, sliced into stories | PRD changes |
| `docs/ROADMAP.md` | Milestones and their order | milestone ends |
| `docs/TASK.md` | Now / Next / Backlog | every session |
| `docs/ARCHITECTURE.md` | How it is built | structure changes |
| `docs/TESTING.md` | What is tested and how to run it | test strategy changes |
| `docs/DEVELOPMENT.md` | Setup, run, troubleshoot | setup steps change |
| `docs/RULES.md` | Deviations from OS standards | a deviation is decided |
| `docs/CHANGELOG.md` | What changed, per version | every user-visible change |
| `docs/decisions/` | ADRs — why things are the way they are | a structural decision is made |
| `docs/memory/STATE.md` | Session snapshot — where we are | see memory rules |
| `docs/memory/DEBT.md` | Shortcuts taken, to be repaid | see memory rules |
| `docs/memory/LESSONS.md` | Hard-won knowledge | see memory rules |

Not applicable to this project (no HTTP API, no database, not yet deployed):
`API_SPEC.md`, `DATABASE.md`, `DEPLOYMENT.md`, `SECURITY.md` — add them the
moment the condition that requires them becomes true (see
`OS_ROOT\standards\documentation.md`).

Update rule: docs change in the **same commit** as the code they describe
(`OS_ROOT\standards\documentation.md`).

## Memory rules

- `docs/memory/` (`STATE.md`, `DEBT.md`, `LESSONS.md`) is the **canonical**
  project memory — committed, survives folder moves and machine changes.
- Claude Code auto-memory (`~/.claude/projects/...`) is scratch — never treat
  it as the source of truth for project state.
- `STATE.md` is a snapshot (overwrite it); `DEBT.md` and `LESSONS.md` are
  append-only.
- At milestone or project end, run `/harvest-lessons` to feed generalizable
  lessons back to the OS.

## Model tiers for this project

- **haiku**: changelogs, doc formatting, mechanical edits from a clear spec.
- **sonnet**: features, tests, bug fixes inside established patterns (default).
- **opus**: architecture, security-sensitive changes, hard debugging.

Escalate a tier when the task changes structure, data models, or auth. The
full cheat sheet lives at `OS_ROOT\HOW_TO_USE.md`.
