# Documentation & Ledger Rules

These rules govern how documentation and the discussion ledger are written
and maintained in this repository. They are intentionally short. When in
doubt, prefer clarity and consistency over cleverness.

## 1. Where things live

- All documentation is Markdown under `docs/`.
- No documentation Markdown lives outside `docs/`, with one exception:
  the top-level `README.md`, which stays minimal and links into `docs/`.
- The discussion ledger lives under `docs/ledger/`.
- Reusable templates live under `docs/templates/`.

## 2. Language

- **Every written record is in English.** Discussions may happen in any
  language (e.g. Romanian), but what gets committed is always English.
- Translate faithfully; do not summarize away meaning when translating.

## 3. Naming

- Files and folders use `kebab-case`: lowercase ASCII, words joined by `-`.
  - Good: `data-ingestion.md`, `why-postgres.md`
  - Bad: `Data Ingestion.md`, `whyPostgres.md`
- File names describe the content, not the date. Dates live inside the file.

## 4. Timestamps

- All timestamps are **UTC** in **ISO 8601**: `YYYY-MM-DDTHH:MM:SSZ`.
  - Example: `2026-06-13T10:20:11Z`.
- Dates without a time use `YYYY-MM-DD`.

## 5. The ledger

The ledger is an append-mostly record of discussions, grouped two ways:

1. **By topic** — one folder per topic under `docs/ledger/`.
2. **By question** — one Markdown file per question inside a topic folder.

Rules:

- One question per file. A file holds the full discussion of that one
  question as a chronological list of timestamped entries.
- **Append, don't rewrite.** Add new entries at the bottom. Do not edit or
  delete past entries; if something was wrong, add a correcting entry.
- Each entry records: timestamp, who/what said it, and the content.
- When a question is settled, set its `Status` to `resolved` in the header
  and, if a decision came out of it, link the decision record.
- Keep a `docs/ledger/README.md` index of topics and open questions.

See `docs/ledger/README.md` for the exact structure and `docs/templates/`
for the entry formats.

## 6. Decisions

- Decisions of lasting consequence get a decision record (ADR-style) under
  `docs/decisions/`, created from `docs/templates/decision-record.md`.
- A decision record is numbered (`0001-...`, `0002-...`) and never deleted;
  superseded ones are marked `superseded` and link to their replacement.

## 7. General writing

- One sentence per line is allowed and encouraged for clean diffs, but not
  required.
- Prefer relative links between docs so they survive moves and clones.
- Keep line length reasonable (~80–100 cols) for readability in diffs.
