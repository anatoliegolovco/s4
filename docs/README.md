# s4 — Documentation

Code name **Sintez 4**.

This directory holds all project documentation as Markdown.

## Layout

| Path | Purpose |
| --- | --- |
| `docs/README.md` | This index. Start here. |
| `docs/RULES.md` | Rules for writing and maintaining docs and the ledger. |
| `docs/templates/` | Reusable templates for docs, decisions, and ledger entries. |
| `docs/ledger/` | Discussion ledger: timestamped Q&A grouped by topic. |

## Conventions (summary)

- **Language:** every written record is in **English**, even when the
  discussion happened in another language.
- **Files and folders:** `kebab-case` (lowercase, words joined by `-`).
- **Timestamps:** UTC, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).

See [`RULES.md`](./RULES.md) for the full set of rules.

## Quick start

1. Adding a normal document? Copy [`templates/doc.md`](./templates/doc.md).
2. Recording a decision? Copy
   [`templates/decision-record.md`](./templates/decision-record.md).
3. Logging a discussion? See [`ledger/README.md`](./ledger/README.md).
