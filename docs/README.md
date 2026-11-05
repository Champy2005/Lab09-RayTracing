# Documentation workspace

## Where things go

| Location | Contents |
| --- | --- |
| `assignment/` | Assignment-source index and space for later course materials |
| `notes/setup.md` | Personal setup template plus assistant-run machine/build record |
| `notes/questions-and-answers.md` | Extra questions, student answers and references |
| `ai/ai-log.md` | One prompt entry per interaction with either AI agent |
| `ai/handoff.md` | Shared handoff template for Codex and Antigravity |
| `ai/transcripts/codex/` | Optional exported Codex/ChatGPT conversations |
| `ai/transcripts/antigravity/` | Optional exported Antigravity/Gemini conversations |
| `report/intermediate-report.md` | Working report, predictions, write-ups and evidence links |
| `report/latex/` | Final report LaTeX source and vector plot assets |
| `report/final/` | Rendered final report PDF |
| `../evidence/` | Saved images, screenshots, terminal captures, tables and plots |

The existing handout remains at the project root. Existing `reference/`, `out/`, and `build/` retain their original roles.

## Suggested recording sequence

1. Fill in your identity and machine information. Record which setup steps you already completed and the evidence for each.
2. Write and date the required predictions in the report before running their experiments. Preserve the original wording, even if it turns out to be wrong.
3. Log every prompt to Codex/ChatGPT or Antigravity/Gemini, including your own idea and verification.
4. For each later experiment, record the command, code revision, settings and evidence IDs. Keep results and explanations blank until you have your own evidence.
5. Save selected outputs from `out/` in `evidence/` before a later run overwrites them. Index them and add a caption explaining what each demonstrates.
6. Complete the Markdown report before requesting LaTeX conversion and final PDF rendering.

The original scaffold was populated by the authorized 2026-11-05 implementation session and finalized on 2026-11-06. The report contains assistant-run measurements; scripts and exact output records are under `../evidence/`. The student's later prediction responses are retained verbatim and dated honestly after measurement. Their personal AI-log reasoning and verification remain separate from assistant checks. The PDF and LaTeX are linked from the project README.

## Placeholder conventions

- `[fill in]` is a field for you to complete.
- `[not run]` means there is no measurement yet.
- `[not recorded]` means the scaffold contains no record of that item.
- `[not supplied]` means a source or chapter extract still needs to be provided.
- An unchecked box is a reminder, not evidence that the underlying work is missing.
- Report question IDs follow the handout: `1.1` through `1.4`, `2.1` through `2.4`, and `3.1` through `3.5`.
- `2.4` and implementation tasks `2c`/`2d` are optional; identify whether you attempted them.
