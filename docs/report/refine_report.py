"""Preserve the student's text and prepare the Markdown report for final typesetting."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/report/intermediate-report.md"


def main():
    original = REPORT.read_text(encoding="utf-8")
    snapshot = ROOT / "evidence/data/report-before-finalization-2026-11-06.md"
    if snapshot.exists():
        original = snapshot.read_text(encoding="utf-8")
    else:
        snapshot.write_text(original, encoding="utf-8")
    prediction_section = original.split("## 2. Predictions recorded before measurement", 1)[1].split("## 3.", 1)[0]
    quotes = re.findall(r"^\u201c.*?\u201d$", prediction_section, re.M)
    if len(quotes) != 5:
        raise ValueError("Expected the student's five original prediction paragraphs")
    record = {
        "recorded_date": "2026-11-06",
        "timezone": "Asia/Bangkok",
        "status": "Later learning exercise; measured experiments preceded these responses.",
        "source": snapshot.relative_to(ROOT).as_posix(),
        "student_text_verbatim": quotes,
    }
    (ROOT / "evidence/data/student-predictions-2026-11-06.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    header = """# Lab 09: Ray Tracing and Path Tracing

**Thanakrit Weeraphatiwat - Student ID 6731323721**
CP479 Computer Graphics - 6 November 2026

## 1. Machine and reproducibility

| Item | Configuration |
| --- | --- |
| CPU / threads | Intel Core Ultra 9 275HX; 24 physical cores, 24 logical threads; 24 render threads |
| OS | Windows 11 Home Single Language, 10.0.26200 |
| Compiler / build | MSVC 19.51.36257.0, x64; C++17; Release |
| CMake / generator | 4.3.1-msvc1 / Visual Studio 18 2026 |
| Build command | `cmake --build build --config Release` |
| Ray / mesh defaults | 800 x 600, vertical FOV 60 degrees, depth 4, EPS 0.001 |
| Path defaults | 256 x 256, 16 spp, depth 64, seed 0, NEE and roulette enabled |
| Timing | Internal render wall time, excluding image saving; three sequential mesh sweeps summarized by their medians; other timings are single runs |

The recorded experiments were run on 5 November 2026. Their source revision, B1, is identified by the [manifest and source snapshots](../../evidence/data/session-manifest.json), based on commit `3d3361d99d412349f20362b4cd324ca9cb407072`. The current three student files differ from B1 only in comments and whitespace. All measurements below are actual runs unless labelled as estimates. Short timings can vary with scheduling, power state and background work.

## 2. Student predictions: later learning exercise

These are the student's original responses, preserved verbatim and recorded on 6 November 2026 (Asia/Bangkok). They were supplied after the 5 November measurements and with AI hints; they are not represented as predictions recorded before measurement. Technical clarifications are separate from the student's words.

### Prediction for 2.1: triangle-count scaling

"""
    prediction_text = header + "\n\n".join("> " + q for q in quotes[:3])
    prediction_text += """

**Technical clarification, 6 November 2026.** With P rays and N triangles, brute-force intersection work is O(PN), or O(N) per ray reaching the mesh. With fixed resolution and ray workload, increasing N therefore gives roughly linear work. BVH traversal can reject entire groups; well-behaved cases often grow approximately logarithmically, but this is not a worst-case guarantee. SAH spends more time building a tree and can reduce triangle work without necessarily minimizing wall time.

### Prediction for 3.1: samples and noise

""" + "> " + quotes[3] + """

**Technical clarification, 6 November 2026.** For independent samples with finite variance, variance of the average falls as 1/N and its standard deviation falls as 1/sqrt(N). The expected log-log noise slope is -0.5, rather than logarithmic decay. Runtime is approximately proportional to spp. RMSE times sqrt(spp) is approximately constant while image sampling noise dominates; the noisy reference and correlation can change this at high spp. Ten times less sampling noise than at 16 spp requires approximately 1600 spp. A different seed changes the noise pattern while preserving its expected distribution.

### Prediction for 3.2: explicit lamp sampling

""" + "> " + quotes[4] + """

**Technical clarification, 6 November 2026.** NEE adds visibility queries but samples the small lamp directly. Without it, each sample can be cheaper, yet many more samples may be needed for a similar error. Equal-spp speed and equal-error efficiency are different comparisons. The measured comparison is reported in write-up 3.2.

"""
    implementation = original.split("## 3. Implementation record", 1)[1].split("## 4.", 1)[0]
    implementation = implementation.replace(
        "The TODO implementations have focused explanations above their functions and important algorithm blocks. A later comment-only cleanup removed inline narration from includes, declarations, and braces; executable code is unchanged. The B1 evidence snapshots retain the original comment style. The six Whitted lessons remain selectable with --stage 1 through --stage 6.",
        "Only student/raytracer.cpp, student/mesh.cpp and student/pathtracer.cpp implement the tasks. Focused comments explain the algorithms. The supplied framework, headers and reference assets are unchanged. Optional BVH traversal is implemented.")
    concepts = """## 3. Implementation and concepts

### Part I: Whitted ray tracing

A camera ray follows p(t) = o + t*d. Sphere intersection solves the quadratic obtained by substituting this ray into the sphere equation. Reflection reverses the normal component of the direction. Refraction uses Snell's law with the index ratio reversed when leaving the object. The recursive colour combines Lambert diffuse, Phong specular, reflected colour and transmitted colour using four material weights. Sided EPS offsets prevent a new ray from immediately hitting its starting surface. Stages 1-6 add flat colour, diffuse, highlights, shadows, reflection and refraction in order.

### Part II: triangles and BVH

Moller-Trumbore solves for distance t and barycentric weights (1-u-v, u, v). The same weights interpolate vertex normals; without vertex normals the geometric face normal is used. Brute force keeps the closest valid triangle. The BVH uses slab-box tests, a fixed depth-first stack, near-child-first ordering and the current closest distance to prune branches. Every tested triangle and popped node is counted.

### Part III: Monte Carlo path tracing

Each camera sample follows one diffuse path. Cosine-weighted sampling uses density cos(theta)/pi, cancelling the Lambert cosine/pi factors so each continuation multiplies throughput by albedo. NEE estimates direct lamp illumination using area, both endpoint cosines, inverse squared distance and visibility. Lamp emission is counted on the front face, and later lamp hits are suppressed with NEE to avoid double counting. From bounce 3, roulette terminates with q = clamp(1 - luminance(throughput), 0.05, 0.95); survivors divide throughput by 1-q. The rule preserves expected future contribution, while the finite depth cap still truncates the path.

"""
    result = prediction_text + concepts + implementation.strip() + "\n\n## 4." + original.split("## 4.", 1)[1].split("## 8. Discussion and learning record", 1)[0]
    result = result.replace("Reflection on the student's original prediction: [student fills in; predictions were deferred].", "**Comparison with the later prediction exercise.** The nearly linear triangle-test slope supports the student's brute-force intuition. BVH growth is much slower over this fixed-view sweep; median/SAH timing depends on the build/traversal tradeoff.")
    result = result.replace("Student prediction/reflection: [left for the student; no prediction was written before these runs].", "**Comparison with the later prediction exercise.** The falling noise and approximately linear runtime match the student's qualitative expectation. The fitted slopes support inverse-square-root decay, rather than logarithmic decay.")
    result = result.replace("Student prediction/reflection: [left for the student].", "**Comparison with the later prediction exercise.** The student's expectation of more speckles without NEE is supported. Lower cost per sample did not compensate for the much larger matching sample count in this experiment.")
    result += """## 8. Evidence and source notes

The [evidence index](../../evidence/README.md) and [run manifest](../../evidence/data/runs.jsonl) retain exact commands, timestamps, panels, image hashes and isolated experimental source changes. Images labelled as renders were generated by the programs; supplied comparison images and the 4096-spp PFM remain under reference/. Figures made from multiple renders are comparison panels, not terminal screenshots. Numerical plots use the recorded CSV data.

Sources are the supplied Lab 09 handout (30 October 2026), the provided core/framework code, the supplied reference assets and the recorded experiments. References to numbered equations use the handout unless explicitly described as chapter equations. The full chapter's Lab 10 listing was not supplied; write-up 3.3 states which conclusions are conditional.

The [consolidated AI prompt log](../ai/ai-log.md) records every prompt available in this session. Exact model labels and student-supplied prompt reasoning/verification were not recorded where indicated; assistant checks are distinguished from student verification. No Antigravity transcript was supplied.
"""
    for quote in quotes:
        assert quote in result, "A student prediction changed"
    REPORT.write_text(result, encoding="utf-8")
    print("Refined report; preserved all five student prediction paragraphs verbatim.")
    print("Student response snapshot:", snapshot)


if __name__ == "__main__":
    main()
