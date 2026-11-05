"""Typeset the refined report as reproducible textbook-style LaTeX and PDF.

Run with the existing Python installation that supplies matplotlib. TeX compilation
uses the installed pdflatex; auxiliary files stay in the ignored build directory.
"""
from pathlib import Path
import csv
import json
import re
import shutil
import subprocess
import textwrap
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/report/intermediate-report.md"
LATEX = ROOT / "docs/report/latex"
BUILD = ROOT / "build/report-latex"
FINAL = ROOT / "docs/report/final/lab09-report.pdf"
REPO = "https://github.com/Champy2005/Lab09-RayTracing"


def wrapped(text):
    return "\n".join("\n".join(part.rstrip() for part in textwrap.wrap(line, width=89, replace_whitespace=False,
                                              drop_whitespace=False, break_on_hyphens=False))
                     for line in plain_unicode(text).splitlines())


def plain_unicode(text):
    replacements = {"\u201c": "``", "\u201d": "''", "\u2018": "`", "\u2019": "'",
                    "\u2013": "--", "\u2014": "---", "\u00d7": " x ", "\u2212": "-",
                    "\u00a0": " ", "\u2264": "<=", "\u2265": ">=", "\u2192": "->"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def escape(text):
    text = plain_unicode(text).replace("\\*", "*")
    special = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%",
               "$": r"\$", "#": r"\#", "_": r"\_", "^": r"\textasciicircum{}", "~": r"\textasciitilde{}",
               "<": r"\ensuremath{<}", ">": r"\ensuremath{>}"}
    result = "".join(special.get(c, c) for c in text)
    return result.replace("/", r"/\allowbreak{}").replace("--", "-{}-")


def link_url(target):
    if "://" in target:
        return target
    path = (REPORT.parent / target.split("#", 1)[0]).resolve()
    try:
        relative = path.relative_to(ROOT).as_posix()
        return REPO + ("/tree/main/" if path.is_dir() else "/blob/main/") + quote(relative)
    except ValueError:
        return target


def inline(text):
    pieces = re.split(r"(`[^`]+`|\[[^\]]+\]\([^\)]+\)|\*\*.+?\*\*)", text)
    out = []
    for part in pieces:
        if part.startswith("`") and part.endswith("`"):
            code = part[1:-1]
            if re.fullmatch(r"[0-9a-f]{32,}", code):
                out.append(r"\texttt{" + r"\allowbreak{}".join(escape(code[i:i+8]) for i in range(0, len(code), 8)) + "}")
            else:
                out.append(r"\texttt{" + escape(code) + "}")
        elif part.startswith("**") and part.endswith("**"):
            out.append(r"\textbf{" + escape(part[2:-2]) + "}")
        elif re.fullmatch(r"\[[^\]]+\]\([^\)]+\)", part):
            match = re.fullmatch(r"\[([^\]]+)\]\(([^\)]+)\)", part)
            out.append(r"\href{" + link_url(match[2]).replace("%", r"\%") + "}{" + escape(match[1]) + "}")
        else:
            out.append(escape(part))
    return "".join(out)


def figure(path, caption, width="0.98", height="0.47"):
    relative = Path(path).relative_to(LATEX).as_posix() if Path(path).is_relative_to(LATEX) else "../../../" + Path(path).relative_to(ROOT).as_posix()
    return (r"\begin{figure}[htbp]\centering" + "\n" +
            rf"\includegraphics[width={width}\linewidth,height={height}\textheight,keepaspectratio]{{\detokenize{{{relative}}}}}" + "\n" +
            r"\caption{" + inline(caption) + "}\n" + r"\end{figure}" + "\n")


def widths(headers):
    joined = " ".join(headers).lower()
    n = len(headers)
    if n == 2:
        return [.26, .74]
    if "implementation and purpose" in joined:
        return [.07, .56, .37]
    if "program / run" in joined:
        return [.13, .22, .08, .25, .32]
    if "both roots" in joined:
        return [.16, .17, .18, .31, .18]
    if "popped nodes" in joined:
        return [.13, .20, .14, .19, .17, .17]
    if "efficiency" in joined:
        return [.30, .10, .10, .13, .13, .14]
    if "approx. relative" in joined:
        return [.10, .12, .20, .37, .21]
    if "seed" in joined and n == 6:
        return [.28, .07, .07, .12, .14, .32]
    if "variant, 64" in joined:
        return [.34, .12, .12, .14, .28]
    if "16384 triangles" in joined:
        return [.31, .27, .21, .21]
    return [1 / n] * n


def table(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in r)]
    headers, body = rows[0], rows[1:]
    spec = "".join(r">{\raggedright\arraybackslash}p{\dimexpr " + f"{w:.4f}" + r"\linewidth-2\tabcolsep\relax}" for w in widths(headers))
    header = " & ".join(r"\textbf{" + inline(c) + "}" for c in headers) + r" \\"
    if len(body) <= 10:
        out = [r"\begin{center}\small\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.14}",
               r"\begin{tabular}{" + spec + "}", r"\toprule", header, r"\midrule"]
        out.extend(" & ".join(inline(c) for c in row) + r" \\" for row in body)
        out.extend([r"\bottomrule\end{tabular}", r"\end{center}"])
        return "\n".join(out) + "\n"
    out = [r"{\small\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.14}", r"\begin{longtable}{" + spec + "}",
           r"\toprule", header, r"\midrule\endfirsthead", r"\toprule", header, r"\midrule\endhead", r"\bottomrule\endfoot"]
    out.extend(" & ".join(inline(c) for c in row) + r" \\" for row in body)
    out.extend([r"\end{longtable}", "}"])
    return "\n".join(out) + "\n"


def terminal(run_id, program):
    text = (ROOT / f"evidence/terminal/{run_id}.txt").read_text(encoding="utf-8")
    body = text.split("Command:", 1)[1].strip()
    lines = [line.rstrip() for line in body.splitlines() if line.strip() and not line.startswith("Exit code:")]
    lines[0] = "> " + lines[0]
    return (r"\needspace{7\baselineskip}\noindent\textbf{" + escape(program + " terminal panel") + "}\n" +
            r"\begin{terminal}" + "\n" + wrapped("\n".join(lines)) + "\n" + r"\end{terminal}" + "\n")


def markdown(text):
    lines = text.splitlines()
    out = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("# ") or line.startswith("**Thanakrit") or line.startswith("CP479 Computer Graphics -"):
            index += 1
            continue
        heading = re.match(r"^(#{2,4})\s+(.+)$", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            if level == 2:
                title = re.sub(r"^\d+\.\s*", "", title)
                out.append(r"\needspace{10\baselineskip}\section{" + escape(title) + "}")
            else:
                out.append(r"\needspace{6\baselineskip}\subsection*{" + escape(title) + "}")
            index += 1
            continue
        if line.startswith("|"):
            block = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index]); index += 1
            out.append(table(block))
            continue
        if line.startswith(">"):
            block = []
            while index < len(lines) and (lines[index].strip().startswith(">") or not lines[index].strip()):
                block.append(re.sub(r"^\s*> ?", "", lines[index])); index += 1
            out.append(r"\begin{quote}\small" + "\n" + markdown("\n".join(block)) + r"\end{quote}")
            continue
        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^\)]+)\)", line)
        if image_match:
            caption, target = image_match.groups()
            path = (REPORT.parent / target).resolve()
            if path.name == "P1-default.png":
                group = [r"\begin{figure}[htbp]\centering"]
                for part, name in [(1, "Whitted, depth 4"), (2, "Mesh, 1024 triangles"), (3, "Cornell, 16 spp")]:
                    relative = f"../../../evidence/images/part-{part}/P{part}-default.png"
                    group += [r"\begin{minipage}[t]{0.325\linewidth}\centering", rf"\includegraphics[width=\linewidth]{{{relative}}}",
                              r"\par\small " + escape(name), r"\end{minipage}"]
                group += [r"\caption{Default outputs from all three programs, with no flags. The ray and mesh images are 800 by 600; the Cornell image is 256 by 256.}", r"\end{figure}"]
                out.append("\n".join(group))
            elif path.name == "P2-default.png":
                pass
            elif path.name == "P3-default.png":
                out.extend(terminal(f"P{part}-default", program) for part, program in [(1, "raytrace"), (2, "mesh"), (3, "pathtrace")])
            elif path.name == "mesh-scaling.png":
                out.append(figure(LATEX / "figures/mesh-time.pdf", "Mesh render time versus triangle count: median of three sequential Release sweeps, 24 threads. Brute-force sizes above 16k were skipped.", "0.88", "0.35"))
                out.append(figure(LATEX / "figures/mesh-tests.pdf", "Triangle tests per primary ray versus triangle count for the same sweep. Both axes use logarithmic scales.", "0.88", "0.35"))
            elif path.name == "path-convergence.png":
                out.append(figure(LATEX / "figures/path-convergence.pdf", caption, "0.88", "0.36"))
            elif path.name == "P1-ior-one.png":
                out.append(r"""\begin{figure}[htbp]\centering
\begin{minipage}[t]{0.49\linewidth}\centering
\includegraphics[width=\linewidth]{../../../evidence/images/part-1/P1-ior-one.png}
\par\small IOR argument changed to 1
\end{minipage}
\begin{minipage}[t]{0.49\linewidth}\centering
\includegraphics[width=\linewidth]{../../../evidence/images/part-1/P1-restored.png}
\par\small Original IOR restored
\end{minipage}
\caption{One-line refraction experiment and restoration. Removing entry/exit bending changes the dark refracted view; restoring the original IOR reproduces the baseline image exactly.}
\end{figure}""")
            elif path.name == "P3-shadow-origin-trap.png":
                # Figure 9 already contains both the correct and trap images at 64 spp.
                pass
            else:
                out.append(figure(path, caption, "0.98", "0.48"))
            index += 1
            continue
        if re.match(r"^\d+\.\s", line) or line.startswith("- "):
            ordered = bool(re.match(r"^\d+\.\s", line))
            environment = "enumerate" if ordered else "itemize"
            out.append(r"\begin{" + environment + "}")
            while index < len(lines):
                item = lines[index].strip()
                if not item:
                    index += 1
                    continue
                match = re.match(r"^\d+\.\s+(.*)$", item) if ordered else re.match(r"^-\s+(.*)$", item)
                if not match:
                    break
                out.append(r"\item " + inline(match[1])); index += 1
            out.append(r"\end{" + environment + "}")
            continue
        paragraph = []
        while index < len(lines) and lines[index].strip():
            if paragraph and re.match(r"^(#{2,4} |\||>|!\[|\d+\. |- )", lines[index].strip()):
                break
            paragraph.append(lines[index].strip()); index += 1
        out.append(inline(" ".join(paragraph)) + "\n\n")
    return "\n".join(out)


def plot_assets():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    folder = LATEX / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "serif", "font.size": 11, "pdf.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})
    rows = list(csv.DictReader((ROOT / "evidence/data/mesh-sweep-medians.csv").open()))
    for key, label, filename in [("render_ms", "Render time (ms)", "mesh-time.pdf"),
                                  ("tests_per_ray", "Triangle tests per primary ray", "mesh-tests.pdf")]:
        fig, ax = plt.subplots(figsize=(6.4, 3.2), layout="constrained")
        for method, style in [("brute force", "o-"), ("bvh median", "s--"), ("bvh sah", "^:")]:
            selected = [r for r in rows if r["method"] == method]
            ax.loglog([int(r["n"]) for r in selected], [float(r[key]) for r in selected], style, label=method)
        ax.set(xlabel="Triangle count N", ylabel=label)
        ax.grid(True, which="both", alpha=.18); ax.legend(fontsize=9)
        fig.savefig(folder / filename); plt.close(fig)
    rows = list(csv.DictReader((ROOT / "evidence/data/path-sweeps.csv").open()))
    fits = json.loads((ROOT / "evidence/data/fits.json").read_text())
    fig, ax = plt.subplots(figsize=(6.4, 3.3), layout="constrained")
    for seed, style in [(0, "o-"), (1, "s--")]:
        selected = [r for r in rows if int(r["seed"]) == seed]
        ax.loglog([int(r["spp"]) for r in selected], [float(r["rmse"]) for r in selected], style,
                  label=f"Seed {seed}, slope {fits[f'path_seed_{seed}']['renderer_log_slope']:.3f}")
    x = np.array([1, 4, 16, 64, 256])
    ax.loglog(x, .082 / np.sqrt(x), ":", color="gray", label="Slope -0.5 guide")
    ax.set(xlabel="Samples per pixel", ylabel="Masked linear-RGB RMSE")
    ax.grid(True, which="both", alpha=.18); ax.legend(fontsize=9)
    fig.savefig(folder / "path-convergence.pdf"); plt.close(fig)


def ai_appendix():
    records = json.loads((ROOT / "docs/ai/prompts.json").read_text(encoding="utf-8"))
    out = [r"\clearpage\appendix\section{AI prompt log}",
           "This appendix contains every available prompt record, including follow-ups. All entries use Codex desktop / Codex assistant. The exact deployed model/version was not exposed; the runtime describes a GPT-6-based agent. Application identity and model identity are distinct. Dates use Asia/Bangkok. Receipt times are unavailable where not explicitly recorded.",
           "Student-supplied idea/prior-knowledge and independent-verification fields were not completed in the available log. They are marked as not recorded, rather than inferred from assistant activity. No Antigravity/Gemini transcript or earlier scaffolding conversation was supplied. The full Markdown log and its original archive are included in the repository."]
    for record in records:
        out += [r"\needspace{8\baselineskip}\subsection*{" + record["id"] + "}",
                r"\noindent\textbf{Date:} " + escape(record["date"]) + r"\par",
                r"\noindent\textbf{Prompt:}", r"\begin{prompt}", wrapped(record["prompt"]), r"\end{prompt}",
                r"\noindent\textbf{Response/work:} " + inline(record["response"]) + r"\par",
                r"\noindent\textbf{Student idea / verification:} Not recorded in the available log.\par\medskip"]
    return "\n".join(out)


def terminal_appendix():
    out = [r"\clearpage\section{Selected terminal evidence}",
           "These are reformatted plain-text program outputs, not screenshots. Blank lines and the local working-directory header are omitted; the command, values and settings are retained. Full dated logs and all 50 run records are included under evidence/."]
    names = ["P1-probe", "P1-skip-zero-weights", "P1-diagnose-tir", "P2-sweep-1", "P2-primary-800",
             "P3-sweep-seed-0", "P3-sweep-seed-1", "P3-no-nee-1792", "P3-rr-first-bounce", "P3-shadow-origin-trap", "P3-lamp-fraction"]
    for name in names:
        content = (ROOT / f"evidence/terminal/{name}.txt").read_text(encoding="utf-8")
        if "Command:" in content:
            content = content.split("Command:", 1)[1].strip()
        lines = [line.rstrip() for line in content.splitlines() if line.strip() and not line.startswith("Exit code:")]
        lines[0] = "> " + lines[0]
        out += [r"\needspace{8\baselineskip}\subsection*{" + escape(name) + "}",
                r"\begin{terminal}", wrapped("\n".join(lines)), r"\end{terminal}"]
    out += [r"\subsection*{Independent geometry and sampling checks}", r"\begin{terminal}",
            (ROOT / "evidence/terminal/verification.txt").read_text().strip(), r"\end{terminal}"]
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=25mm]{geometry}
\usepackage{graphicx,amsmath,amssymb,booktabs,longtable,array}
\usepackage{caption,needspace,fancyhdr,fancyvrb}
\usepackage[hidelinks]{hyperref}
\hypersetup{pdftitle={Lab 09: Ray Tracing and Path Tracing},pdfauthor={Thanakrit Weeraphatiwat},pdfsubject={CP479 Computer Graphics lab report}}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyfoot[L]{\small CP479: Computer Graphics}
\fancyfoot[R]{\small Page \thepage\ of \pageref{report-last-page}}
\setlength{\headheight}{14pt}
\setlength{\parskip}{4pt}
\setlength{\parindent}{1em}
\setlength{\emergencystretch}{3em}
\setlength{\LTpre}{5pt}
\setlength{\LTpost}{5pt}
\captionsetup{font=small,labelfont=bf}
\DefineVerbatimEnvironment{terminal}{Verbatim}{fontsize=\footnotesize,frame=single,framesep=2mm}
\DefineVerbatimEnvironment{prompt}{Verbatim}{fontsize=\footnotesize}
\begin{document}
\begin{center}
{\Large Lab 09: Ray Tracing and Path Tracing}\par\medskip
CP479 Computer Graphics\par
Thanakrit Weeraphatiwat\quad Student ID 6731323721\par
6 November 2026
\end{center}
\vspace{2mm}
"""


def main():
    LATEX.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    plot_assets()
    report = REPORT.read_text(encoding="utf-8")
    tex = PREAMBLE + markdown(report) + ai_appendix() + terminal_appendix() + "\n" + r"\label{report-last-page}\end{document}" + "\n"
    source = LATEX / "lab09-report.tex"
    source.write_text(tex, encoding="utf-8")
    command = ["pdflatex", "--disable-installer", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
               f"-output-directory={BUILD}", source.name]
    logs = []
    for number in (1, 2):
        result = subprocess.run(command, cwd=LATEX, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.stdout.decode("utf-8", errors="replace")
        logs.append(f"PASS {number}: " + subprocess.list2cmdline(command) + "\n" + output)
        if result.returncode:
            (ROOT / "evidence/terminal/final-report-latex-build.txt").write_text("\n\n".join(logs), encoding="utf-8")
            print(output[-14000:])
            raise SystemExit(result.returncode)
    (ROOT / "evidence/terminal/final-report-latex-build.txt").write_text("\n\n".join(logs), encoding="utf-8")
    shutil.copy2(BUILD / "lab09-report.pdf", FINAL)
    print("LaTeX:", source)
    print("PDF:", FINAL)
    print("\n".join(line for line in logs[-1].splitlines() if "Overfull" in line or "Warning" in line or "Output written" in line))


if __name__ == "__main__":
    main()
