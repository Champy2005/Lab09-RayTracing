# AI prompt log

Shared log for Codex / ChatGPT and Antigravity / Gemini. Entries below cover the user instructions and prompts visible during this implementation session. Historical scaffolding prompts were not available here and must be added by the student if applicable. Automatic empty Page-context messages are UI metadata, not separate coding prompts.

The student supplies the idea behind each prompt and their own verification. These fields remain unfilled; assistant-run checks do not mark them verified.

## Agent/model register

| Application / agent | Provider / model family | Exact deployed model/version | Session |
| --- | --- | --- | --- |
| Codex desktop / Codex assistant | OpenAI; runtime describes the agent as based on GPT-6 | Not exposed to the assistant; student should record the UI model label, without guessing | 2026-11-05 |
| Antigravity / Gemini | Google | Not recorded; not used by this Codex session | [student fills if used] |

## Prompt index

Prompt receipt times are not exposed. All visible prompts are dated 2026-11-05 (Asia/Bangkok); the entries were recorded at 2026-11-05T20:37:39+07:00.

| ID | Purpose | Full entry | Student verification |
| --- | --- | --- | --- |
| AI-C-000 | Workspace instructions | [Entry](#ai-c-000) | Not supplied by student |
| AI-C-001 | Implementation and report | [Entry](#ai-c-001) | Not supplied by student |
| AI-C-002 | Missing chapter source | [Entry](#ai-c-002) | Not supplied by student |
| AI-C-003 | Clarification about provided material | [Entry](#ai-c-003) | Not supplied by student |
| AI-C-004 | Answer from available Part III | [Entry](#ai-c-004) | Not supplied by student |

| AI-C-005 | Quick guided walkthrough | [Entry](#ai-c-005) | Not supplied by student |

| AI-C-006 | Comment cleanup | [Entry](#ai-c-006) | Not supplied by student |

| AI-C-007 | Standalone comments | [Entry](#ai-c-007) | Not supplied by student |

| AI-C-008 | Detailed Part I walkthrough | [Entry](#ai-c-008) | Not supplied by student |

| AI-C-009 | Questions beside report answers | [Entry](#ai-c-009) | Not supplied by student |

| AI-C-010 | Simpler question wording | [Entry](#ai-c-010) | Not supplied by student |

| AI-C-011 | Part I write-up guidance | [Entry](#ai-c-011) | Not supplied by student |

| AI-C-012 | Refresh simpler questions | [Entry](#ai-c-012) | Not supplied by student |

| AI-C-013 | Hints for deferred predictions | [Entry](#ai-c-013) | Not supplied by student |

## AI-C-000

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-05, Asia/Bangkok; exact receipt time unavailable.
- Working revision: base 3d3361d99d412349f20362b4cd324ca9cb407072 plus uncommitted B1 source; see [manifest](../../evidence/data/session-manifest.json).
- Task: Workspace instructions.

### Exact prompt

```text
# Shared project guidance

Applies to Codex/ChatGPT and Antigravity/Gemini, and to other assistants working here.

## Current phase

The user has requested documentation scaffolding only. Until the user explicitly requests further work, add or maintain boilerplate, questions and empty recording fields only. Do not implement tasks, answer report questions, write predictions for the student, run builds or experiments, install dependencies, or generate final LaTeX/PDF artifacts.

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
```

### Idea behind my prompt (student fills this)

- What I needed and what I already knew/tried: [student fills in].
- Why I phrased the prompt this way: [student fills in].

### Assistant response / work performed

Loaded project scope, preservation rules, evidence rules, and AI-log requirements.

Relevant work: [intermediate report](../report/intermediate-report.md), [evidence index](../../evidence/README.md), [checks](../../evidence/terminal/verification.txt).

### Verification (student fills this)

- Claim/change I checked: [student fills in].
- My method and why it is relevant: [student fills in].
- Exact command / hand calculation / comparison: [student fills in].
- Evidence and actual outcome: [student fills in].
- Limits / what I can explain in my own words: [student fills in].
- Status: not yet supplied by student.

## AI-C-001

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-05, Asia/Bangkok; exact receipt time unavailable.
- Working revision: base 3d3361d99d412349f20362b4cd324ca9cb407072 plus uncommitted B1 source; see [manifest](../../evidence/data/session-manifest.json).
- Task: Implementation and report.

### Exact prompt

```text
Help me implement all parts, comment explain every line what it does, fill write-ups in the intermediate markdown, skip the predictions I will answer them later myself. I don't have much time to do this lab, so after you finish those things I will ask you to quickly guide me through this lab and what it want to teach me.
```

### Idea behind my prompt (student fills this)

- What I needed and what I already knew/tried: [student fills in].
- Why I phrased the prompt this way: [student fills in].

### Assistant response / work performed

Implemented tasks 1a-3d including optional BVH, commented student source, built/checked it, ran measured experiments, and filled the intermediate report. Prediction fields were preserved. Original student code was backed up.

Relevant work: [intermediate report](../report/intermediate-report.md), [evidence index](../../evidence/README.md), [checks](../../evidence/terminal/verification.txt).

### Verification (student fills this)

- Claim/change I checked: [student fills in].
- My method and why it is relevant: [student fills in].
- Exact command / hand calculation / comparison: [student fills in].
- Evidence and actual outcome: [student fills in].
- Limits / what I can explain in my own words: [student fills in].
- Status: not yet supplied by student.

## AI-C-002

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-05, Asia/Bangkok; exact receipt time unavailable.
- Working revision: base 3d3361d99d412349f20362b4cd324ca9cb407072 plus uncommitted B1 source; see [manifest](../../evidence/data/session-manifest.json).
- Task: Missing chapter source.

### Exact prompt

```text
I think the report might be misleading or something like cause this is lab9. no lab10 mentioned in the pdf instruction so I think it might be some misleading or something.
```

### Idea behind my prompt (student fills this)

- What I needed and what I already knew/tried: [student fills in].
- Why I phrased the prompt this way: [student fills in].

### Assistant response / work performed

Explained that page 14 question 3.3 references a separate chapter listing, while this assignment is Lab 09. Continued the available experiments.

Relevant work: [intermediate report](../report/intermediate-report.md), [evidence index](../../evidence/README.md), [checks](../../evidence/terminal/verification.txt).

### Verification (student fills this)

- Claim/change I checked: [student fills in].
- My method and why it is relevant: [student fills in].
- Exact command / hand calculation / comparison: [student fills in].
- Evidence and actual outcome: [student fills in].
- Limits / what I can explain in my own words: [student fills in].
- Status: not yet supplied by student.

## AI-C-003

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-05, Asia/Bangkok; exact receipt time unavailable.
- Working revision: base 3d3361d99d412349f20362b4cd324ca9cb407072 plus uncommitted B1 source; see [manifest](../../evidence/data/session-manifest.json).
- Task: Clarification about provided material.

### Exact prompt

```text
oh I just found it in the instruction pdf, I don't know like I've be given only the lab9 repo, maybe its like cut the question from textbooks or something.
```

### Idea behind my prompt (student fills this)

- What I needed and what I already knew/tried: [student fills in].
- Why I phrased the prompt this way: [student fills in].

### Assistant response / work performed

Acknowledged that the separate chapter source was unavailable; did not invent its contents or claim to compile it.

Relevant work: [intermediate report](../report/intermediate-report.md), [evidence index](../../evidence/README.md), [checks](../../evidence/terminal/verification.txt).

### Verification (student fills this)

- Claim/change I checked: [student fills in].
- My method and why it is relevant: [student fills in].
- Exact command / hand calculation / comparison: [student fills in].
- Evidence and actual outcome: [student fills in].
- Limits / what I can explain in my own words: [student fills in].
- Status: not yet supplied by student.

## AI-C-004

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-05, Asia/Bangkok; exact receipt time unavailable.
- Working revision: base 3d3361d99d412349f20362b4cd324ca9cb407072 plus uncommitted B1 source; see [manifest](../../evidence/data/session-manifest.json).
- Task: Answer from available Part III.

### Exact prompt

```text
but like it might be just the skew lab number like if all the parts or the part 3 path tracing  can be referred then answer it if not then just explain that we can't referrence it.
```

### Idea behind my prompt (student fills this)

- What I needed and what I already knew/tried: [student fills in].
- Why I phrased the prompt this way: [student fills in].

### Assistant response / work performed

Answered question 3.3 using this repository's actual Hit/emission and path-tracer flow, with explicit conditional reasoning where the quoted chapter excerpt does not provide enough code. Measured a first-bounce roulette variant.

Relevant work: [intermediate report](../report/intermediate-report.md), [evidence index](../../evidence/README.md), [checks](../../evidence/terminal/verification.txt).

### Verification (student fills this)

- Claim/change I checked: [student fills in].
- My method and why it is relevant: [student fills in].
- Exact command / hand calculation / comparison: [student fills in].
- Evidence and actual outcome: [student fills in].
- Limits / what I can explain in my own words: [student fills in].
- Status: not yet supplied by student.

## Entry template: [AI ID]

### Identity and context

- Date/time and timezone: [fill in]
- Application / agent: [fill in]
- Exact model/version: [fill in]
- Session / conversation reference: [fill in]
- Task / report question: [fill in]
- Code revision / working-tree context: [fill in]
- Files or materials supplied to the agent: [fill in]

### Exact prompt

```text
[paste the complete prompt here]
```

### Idea behind my prompt (student fills this)

- What did I need help with? [fill in]
- What did I already know or try? [fill in]
- Why did I ask this question in this way? [fill in]

### Response and what I used

- Response summary / optional transcript link: [fill in]
- Suggestions I accepted: [fill in]
- Suggestions I changed or rejected, and why: [fill in]
- Files affected / diff or revision reference: [fill in]
- What I can explain in my own words: [fill in]

### Verification (student fills this)

- What claim or change did I check? [fill in]
- My verification method and why it is relevant: [fill in]
- Exact command, hand calculation or comparison: [fill in]
- Evidence IDs / reference images / source pages: [fill in]
- Actual outcome: [fill in]
- Limitations and remaining uncertainty: [fill in]
- Status (not checked / supported / contradicted / inconclusive): [fill in]

### Follow-up

- Related earlier or later prompt IDs: [fill in]
- Next question for me to resolve: [fill in]

Copy the entry template for every prompt to either agent. Optional exports belong in `transcripts/codex/` or `transcripts/antigravity/`.

## AI-C-005

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; runtime describes a GPT-6-based agent. Student supplies the UI label.
- Recorded: 2026-11-05T22:29:34+07:00.
- Task: guided explanation of concepts, code, predictions and write-ups.

### Exact prompt

```text
ok now guiding me to this lab real quick, like concept, todo, codes, prediction and write-up, teach me.
```

### Idea behind my prompt (student fills this)

[student fills in what they needed and already knew]

### Assistant response / work performed

Explained the ray model, Whitted shading, triangle intersection/BVH, Monte Carlo paths, throughput, cosine sampling, NEE and roulette; connected them to existing functions and report experiments. Included a short practice checklist. Predictions remain untouched; distinguished later learning exercises from predictions before the already completed measurements.

### Verification (student fills this)

- My own explanation / command / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-006

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Recorded: 2026-11-05T22:33:11+07:00.

### Exact prompt

```text
also like before going next, i just read you code, and you literally comment every line like i said, like I meant comment it in detail only on the todos. can you clean thing up? like keep only comment/explanation on those todo.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Removed line-by-line narration from the three student implementations. Retained focused TODO explanations above functions and important algorithm blocks; no trailing inline comments remain. Verified that executable code is identical after excluding comments and whitespace. Updated the report's description of the comment style; historical experiment snapshots remain preserved.

### Verification (student fills this)

- My checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-007

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Recorded: 2026-11-05T22:33:11+07:00.

### Exact prompt

```text
also make comment upper or under cause it's so hard to read in one long line.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Removed line-by-line narration from the three student implementations. Retained focused TODO explanations above functions and important algorithm blocks; no trailing inline comments remain. Verified that executable code is identical after excluding comments and whitespace. Updated the report's description of the comment style; historical experiment snapshots remain preserved.

### Verification (student fills this)

- My checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-008

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Recorded: 2026-11-05T22:40:20+07:00.

### Exact prompt

```text
ok now focus on part 1, guide me through it in detail.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Read current Part I implementation and framework types/intersection code. Explained camera projection, quadratic sphere roots, surface normals, reflection, Snell refraction, Lambert/Phong lighting, visibility, sided EPS offsets, recursive material weights and stage controls. Connected these to existing measured Part I write-ups and suggested comprehension exercises. No implementations or predictions were changed and no experiments were run.

### Verification (student fills this)

- My explanation / checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-009

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-06, Asia/Bangkok; exact prompt receipt time unavailable.

### Exact prompt

```text
can you add questions to every write-up on the report? like i have to swithc back and forth to know the context.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Added a clearly labelled paraphrase of the relevant handout question above each of the 13 write-up answers (1.1-1.4, 2.1-2.4 and 3.1-3.5), with source page numbers and an Answer and evidence label. Included the student's existing missing-chapter clarification in 3.3. Verified that removing the inserted blocks restores the previous report content exactly, before the update-date change; predictions and answers were preserved. No builds or experiments were run.

### Verification (student fills this)

- My checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-010

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-06, Asia/Bangkok; exact prompt receipt time unavailable.

### Exact prompt

```text
yeah also would be very great if you rephrase those questions a bit while retain the core meaning, cause it so hard to understand and make my headache.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Rewrote all 13 question blocks in plain English as short numbered steps. Explained essential terms while preserving commands, required comparisons, equations, calculations, optional BVH status and the missing-chapter qualification. Verified that every part outside the question blocks, including all answers and prediction fields, remains unchanged. No builds or experiments were run.

### Verification (student fills this)

- My checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-011

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-06, Asia/Bangkok; exact prompt receipt time unavailable.

### Exact prompt

```text
ok now guid me on the part 1 write ups
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Guided the student through write-ups 1.1-1.4: quadratic coefficients and roots, EPS/self-intersection and scene units, depth/ray counts and zero-weight branches, and the measured glass-wedge/IOR experiment. Used existing measurements and distinguished them from proposed student checks. No report answers, predictions or source files were changed; no new experiments were run.

### Verification (student fills this)

- My explanation / checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-012

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-06, Asia/Bangkok; exact prompt receipt time unavailable.

### Exact prompt

```text
uh somehow the report just revert back to the version before the rephrased questions, can you rephrase it again?
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

The file on disk still contained the previous numbered plain-language questions; the cause of the user's older view was not established. Simplified all 13 question blocks further, saved the report again, and read it back to confirm persistence. Verified all content outside the question blocks, including answers and predictions, was unchanged. No builds or experiments were run.

### Verification (student fills this)

- My checks / evidence / outcome: [student fills in].
- Status: not yet supplied by student.

## AI-C-013

- Application / agent: Codex desktop / Codex assistant.
- Exact model/version: not exposed; see model register.
- Date: 2026-11-06, Asia/Bangkok; exact receipt time unavailable.

### Exact prompt

```text
ok I don't have much time now, Im going to bed soon, can you help me quickly do the predictions? like hint me how to answer them like what part 2 and 3 is yet.
```

### Idea behind my prompt (student fills this)

[student fills in]

### Assistant response / work performed

Provided a short introduction to triangle meshes/BVH and Monte Carlo path tracing, then conceptual hints and incomplete sentence starters for prediction sections 2.1, 3.1 and 3.2. Explained that experiments already ran and later answers must be honestly labelled as a learning exercise. Did not fill prediction fields or invent the student's reasoning.

### Verification (student fills this)

- My reasoning / checks / outcome: [student fills in].
- Status: not yet supplied by student.
