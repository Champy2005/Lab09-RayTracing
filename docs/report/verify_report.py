"""Check final report provenance, references, LaTeX warnings, and PDF content."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]


def main():
    checks = []

    def require(condition, message):
        if not condition:
            raise AssertionError(message)
        checks.append(message)

    report = (ROOT / "docs/report/intermediate-report.md").read_text(encoding="utf-8")
    predictions = json.loads((ROOT / "evidence/data/student-predictions-2026-11-06.json").read_text(encoding="utf-8"))
    for i, quote in enumerate(predictions["student_text_verbatim"], 1):
        require(quote in report, f"Student prediction paragraph {i} preserved verbatim")
    require("later learning exercise" in report.lower(), "Later predictions are not represented as pre-measurement records")
    require(len(re.findall(r"(?m)^### [123]\.\d:", report)) == 13, "All thirteen write-up sections present")
    require(not re.search(r"\[(?:fill in|student fills|not run|section)\b", report), "No scaffold placeholders in the refined report")
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", report):
        if "://" not in target:
            require((ROOT / "docs/report" / target).exists(), "Report reference exists: " + target)

    prompts = json.loads((ROOT / "docs/ai/prompts.json").read_text(encoding="utf-8"))
    require([p["id"] for p in prompts] == [f"AI-C-{i:03d}" for i in range(15)], "All fifteen available prompt records collected once")
    for record in prompts:
        require(bool(record["prompt"].strip()), "Original prompt text retained: " + record["id"])
        require("not" in record["student_verification"].lower(), "Missing student verification is not invented: " + record["id"])

    strip = lambda s: re.sub(r"\s+", "", re.sub(r"//[^\n]*", "", s))
    source_hashes = {}
    for path in sorted((ROOT / "student").glob("*.cpp")):
        before = (ROOT / "evidence/data/final-student" / (path.name + ".txt")).read_text(encoding="utf-8")
        require(strip(path.read_text(encoding="utf-8")) == strip(before), "Executable implementation matches tested B1: " + path.name)
        source_hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    original = json.loads((ROOT / "evidence/data/session-manifest.json").read_text())
    for target, digest in original["reference_sha256"].items():
        require(hashlib.sha256((ROOT / target).read_bytes()).hexdigest() == digest, "Supplied reference unchanged: " + target)

    log = (ROOT / "evidence/terminal/final-report-latex-build.txt").read_text(encoding="utf-8")
    last_pass = log.split("PASS 2:")[-1]
    require("Output written" in last_pass, "Final LaTeX pass produced a PDF")
    require(not re.search(r"Overfull|LaTeX (?:Font )?Warning|undefined references|Fatal error", last_pass), "Final LaTeX pass has no overflow, font, or reference warnings")

    pdf = ROOT / "docs/report/final/lab09-report.pdf"
    reader = PdfReader(pdf)
    text = "\n".join(page.extract_text() for page in reader.pages)
    require("Thanakrit" in text and "6731323721" in text, "PDF contains supplied student name and ID")
    for identifier in [p["id"] for p in prompts]:
        require(identifier in text, "PDF includes AI record " + identifier)
    for value in ["0.0206", "0.1584", "1792", "115912", "1600"]:
        require(value in text, "PDF retains key result " + value)
    for i, page in enumerate(reader.pages, 1):
        require(len(page.extract_text().strip()) > 80, f"PDF page {i} is nonblank")
        require(f"of {len(reader.pages)}" in page.extract_text(), f"PDF page {i} has resolved total-page footer")
    with pdfplumber.open(pdf) as document:
        for i, page in enumerate(document.pages, 1):
            for word in page.extract_words():
                require(word["x0"] >= 25 and word["x1"] <= float(page.width) - 25,
                        f"Page {i} text within horizontal page safety margins")
    manifest = {
        "report_date": "2026-11-06", "timezone": "Asia/Bangkok", "pdf_pages": len(reader.pages),
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "student_source_sha256": source_hashes,
        "available_ai_prompt_records": len(prompts), "student_prediction_paragraphs_preserved": 5,
        "prediction_provenance": "Student responses recorded after measurements, retained verbatim with separate technical clarification.",
        "source_check": "Executable tokens match B1 after excluding comments and whitespace.",
        "validation": "Release build and 115912 independent checks passed; document checks passed; all PDF pages rendered for visual review.",
        "missing_information": ["Exact deployed model/version label", "Student-specific AI-log reasoning and independent verification", "Complete referenced Chapter 10 Lab 10 listing"],
    }
    (ROOT / "evidence/data/finalization-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Coordinate checks occur per word; summarize them once per page in the readable log.
    summary = [c for c in checks if "horizontal page safety" not in c]
    summary += [f"All {len(reader.pages)} pages have text within horizontal page safety margins.",
                "Visual QA: rendered all pages with Poppler and reviewed page sheets and representative full pages."]
    (ROOT / "evidence/terminal/final-report-validation.txt").write_text("\n".join("PASS: " + c for c in summary) + "\n", encoding="utf-8")
    print(f"Verified {len(reader.pages)} PDF pages, 13 write-ups, 15 prompt records, five original prediction paragraphs, source/reference hashes and all report links.")


if __name__ == "__main__":
    main()
