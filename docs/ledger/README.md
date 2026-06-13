# Discussion Ledger

A timestamped record of project discussions, decisions-in-progress, and the
reasoning behind them. The ledger is the project's memory.

## How it is organized

```
docs/ledger/
├── README.md            ← this index
└── <topic>/             ← one folder per topic
    ├── README.md        ← topic index (questions table)
    └── <question>.md    ← one file per question, chronological entries
```

- **By topic:** each topic is a folder.
- **By question:** each question is a file inside its topic folder.
- Inside a question file, the discussion is a list of **timestamped entries**
  (UTC, ISO 8601), appended newest-at-the-bottom.

## How to add to the ledger

1. Pick or create a topic folder under `docs/ledger/`.
   - New topic? Copy [`../templates/ledger-topic.md`](../templates/ledger-topic.md)
     to `docs/ledger/<topic>/README.md`.
2. Pick or create the question file.
   - New question? Copy
     [`../templates/ledger-question.md`](../templates/ledger-question.md)
     to `docs/ledger/<topic>/<question>.md`.
3. Append your entry under `## Discussion` with a UTC timestamp.
4. Update the topic index table and the table below.

Rules: append, don't rewrite; English only; `kebab-case` names. Full rules in
[`../RULES.md`](../RULES.md).

## Topics

| Topic | Status | Description |
| --- | --- | --- |
| [`project-setup`](./project-setup/README.md) | active | Repository, docs, and tooling setup. |

## Open questions (across all topics)

| Topic | Question | Opened |
| --- | --- | --- |
| project-setup | [Documentation & ledger structure](./project-setup/documentation-structure.md) | 2026-06-13 (resolved) |
