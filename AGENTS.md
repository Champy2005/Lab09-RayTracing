# Shared project guidance

Applies to Codex/ChatGPT and Antigravity/Gemini, and to other assistants working here.

## Current phase

The user subsequently authorized implementation, experiments and write-ups, and on 2026-11-06 explicitly requested final report refinement, AI-log collection, LaTeX/PDF generation, and committing/pushing to the existing GitHub repository. Preserve the student's original later prediction responses verbatim and keep technical clarification separate. Do not fabricate pre-measurement predictions, exact model labels, or student-specific reasoning/verification that was not supplied.

## Preserve the student's work

- Read the current files and the latest user instructions before making changes.
- Keep existing source, build configuration, editor settings, handout, reference assets and outputs in place during documentation setup.
- Do not infer successful setup, measurements or verification from the presence of files.
- Keep student-authored predictions unchanged after measurement; append a dated reflection separately.
- Leave the student's reasoning, answers, observations and verification fields for the student to fill.
- When implementation is later requested, consult the handout's scope: the submitted source edits belong in `student/raytracer.cpp`, `student/mesh.cpp`, and `student/pathtracer.cpp`.

## Two-agent records

- Use `docs/ai/ai-log.md` as the shared prompt log, with one entry for every prompt to either agent.
- Identify the application/agent and exact model separately; do not guess model versions.
- The student supplies the idea behind each prompt and how the answer was verified. Do not invent these entries or mark them verified on the student's behalf.
- Keep optional raw transcripts under `docs/ai/transcripts/codex/` or `docs/ai/transcripts/antigravity/`; link them from the log.
- Read and update `docs/ai/handoff.md` when handing work between agents. Record touched files, pending questions and proposed next work.
- Avoid simultaneous edits to the same file. If another agent has edited a file, reread it and preserve its changes.
- Do not claim that a handoff note sends a message or synchronizes applications automatically.

## Documentation and evidence

- The working report is `docs/report/intermediate-report.md`.
- Save predictions in the report before the relevant measurements, with time and revision references.
- Save selected evidence under `evidence/` and index it in `evidence/README.md`. `out/` is ignored and may be overwritten by later runs.
- Distinguish planned commands from executed commands, predictions from observations, and supplied reference images from student-generated outputs.
- Never fabricate images, terminal captures, measurements, citations or results.
- Use paths relative to each Markdown file for embedded evidence. Leave unavailable image embeds as commented examples until the file exists.
- Leave `docs/report/latex/` and `docs/report/final/` empty until finalization is requested.

Later explicit user instructions can change the current phase or scope.
