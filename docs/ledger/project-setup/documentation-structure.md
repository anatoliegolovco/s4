# Q: How should docs and the discussion ledger be structured?

- **Topic:** project-setup ([index](./README.md))
- **Status:** resolved
- **Opened:** 2026-06-13T10:20:11Z
- **Resolved:** 2026-06-13T10:20:11Z
- **Decision:** —

## Context

The s4 ("Sintez 4") repository started essentially empty. Before the first
technical task, we need a home for documentation and a durable record of
discussions, so reasoning is not lost between sessions.

## Discussion

### 2026-06-13T10:20:11Z — user

Requested: create a `docs/` directory and keep all Markdown there. Keep a
discussion ledger with date-time under `docs/ledger/`, grouped by topics and
by questions. Generate templates and rules. Note: discussion may happen in
Romanian, but everything written down must be in English. A technical task
will follow.

### 2026-06-13T10:20:11Z — claude

Implemented the structure:

- `docs/README.md` — documentation index.
- `docs/RULES.md` — rules for docs and the ledger (location, language,
  naming, timestamps, append-only ledger, decisions).
- `docs/templates/` — `doc.md`, `decision-record.md`, `ledger-topic.md`,
  `ledger-question.md`.
- `docs/ledger/` — ledger root with `README.md`, the `project-setup` topic,
  and this question file as the first entry.

Key conventions chosen: English-only written records; `kebab-case` names;
UTC ISO 8601 timestamps; ledger grouped by topic (folder) then question
(file); append-only entries.

## Outcome

The documentation and ledger structure is in place and documented in
`docs/README.md` and `docs/RULES.md`. Ready for the upcoming technical task,
which will open new topics/questions in the ledger as needed.
