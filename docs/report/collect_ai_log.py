"""Consolidate available prompt records without inventing student reasoning."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "docs/ai/ai-log.md"
PROMPT = """Here, I just answer them, can you finish thing off? collect all the ai logs, refine report, and then make the final report latex and render it to pdf. and then commit and push to code to github repo. the final report doesn't have to be fancy, like just copy the instruction pdf style, minimal textbook style. don't have add those much introduction things, just core reports, write ups, predictions, eveidences, results from terminal, images, ai logs, and may be add some detail on concept like how each part/subpart work, or how we implement them, etc."""


def section(text, names):
    for name in names:
        match = re.search(r"(?ms)^### " + re.escape(name) + r"\s*\n(.*?)(?=^### |\Z)", text)
        if match:
            return match.group(1).strip()
    return ""


def main():
    source = LOG.read_text(encoding="utf-8")
    snapshot = ROOT / "evidence/data/ai-log-before-finalization-2026-11-06.md"
    if not snapshot.exists():
        snapshot.write_text(source, encoding="utf-8")
    records = []
    for match in re.finditer(r"(?ms)^## (AI-C-\d{3})\s*\n(.*?)(?=^## AI-C-\d{3}|\Z)", source):
        identifier, entry = match.groups()
        entry = entry.split("## Entry template:", 1)[0]
        prompt = re.search(r"(?s)### Exact prompt\s*\n\s*```text\n(.*?)\n```", entry)
        if not prompt:
            raise ValueError("Missing original prompt: " + identifier)
        date = re.search(r"(?m)^- (?:Recorded|Date|Date/time and timezone):\s*(.*)", entry)
        records.append({
            "id": identifier,
            "date": date.group(1).rstrip(".") if date else "2026-11-05; exact receipt time unavailable",
            "application": "Codex desktop / Codex assistant",
            "model": "Exact deployed model/version not exposed; runtime describes a GPT-6-based agent",
            "prompt": prompt.group(1),
            "response": section(entry, ["Assistant response / work performed", "Assistant response / work performed", "Response and what I used"]),
            "student_reasoning": "Not recorded by the student in the available log.",
            "student_verification": "Not recorded by the student in the available log.",
        })
    if not any(r["id"] == "AI-C-014" for r in records):
        records.append({
            "id": "AI-C-014", "date": "2026-11-06, Asia/Bangkok; exact prompt receipt time unavailable",
            "application": "Codex desktop / Codex assistant",
            "model": "Exact deployed model/version not exposed; runtime describes a GPT-6-based agent",
            "prompt": PROMPT,
            "response": "Finalization request: preserve the supplied prediction responses, refine the report, consolidate available AI records, prepare minimal textbook-style LaTeX and its rendered PDF, verify the deliverables, and commit/push the implementation and report. Source artifacts and verification records accompany the report; publication is recorded in the repository history.",
            "student_reasoning": "Not recorded separately from the explicit request.",
            "student_verification": "Not recorded by the student in the available log.",
        })
    records.sort(key=lambda r: r["id"])
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("Duplicate prompt IDs")
    title = """# Consolidated AI prompt log

Available prompts from the Codex sessions on 5-6 November 2026 (Asia/Bangkok), in chronological prompt-ID order. Automatic empty Page-context messages are UI metadata. Earlier scaffolding conversations and Antigravity/Gemini transcripts were not supplied, so their contents are not reconstructed.

Application and model are separate fields. The exact deployed model/version was not exposed; the runtime describes Codex as GPT-6-based. No more precise model label is guessed. The original pre-finalization log is retained under evidence/data/ai-log-before-finalization-2026-11-06.md.

Student reasoning and independent verification are identified as not recorded where they were not supplied. Assistant-run build, geometric checks and image/measurement comparisons are linked in the response summaries; they do not establish student verification.

## Prompt index

| ID | Date / timezone | Entry |
| --- | --- | --- |
"""
    out = title + "\n".join(f"| {r['id']} | {r['date']} | [Entry](#{r['id'].lower()}) |" for r in records) + "\n"
    for r in records:
        out += f"\n## {r['id']}\n\n- Application / agent: {r['application']}.\n- Model: {r['model']}.\n- Date: {r['date']}.\n\n### Exact prompt\n\n```text\n{r['prompt']}\n```\n\n### Student idea / prior knowledge\n\n{r['student_reasoning']}\n\n### Assistant response / work performed\n\n{r['response']}\n\n### Student verification\n\n{r['student_verification']}\n"
    LOG.write_text(out, encoding="utf-8")
    (ROOT / "docs/ai/prompts.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Consolidated {len(records)} prompt records; preserved original prompts and the prior log.")


if __name__ == "__main__":
    main()
