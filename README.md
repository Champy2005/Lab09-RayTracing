# Lab 09: Ray Tracing and Path Tracing

CP479 Computer Graphics. Implemented C++17 ray tracing, mesh intersection/BVH, and path tracing, with an AI-assisted intermediate report and retained experiment evidence.

## Start here

- [Final report (PDF)](docs/report/final/lab09-report.pdf)
- [LaTeX source](docs/report/latex/lab09-report.tex)
- [Lab handout](instructions-1032980-17933293399497.pdf)
- [Workspace and evidence guide](docs/README.md)
- [Setup record](docs/notes/setup.md)
- [Intermediate report](docs/report/intermediate-report.md)
- [AI prompt log: both agents](docs/ai/ai-log.md)
- [Agent handoff](docs/ai/handoff.md)
- [Extra questions and answers](docs/notes/questions-and-answers.md)
- [Evidence index](evidence/README.md)

## Existing project layout

| Path | Purpose |
| --- | --- |
| `student/` | Implemented tasks 1a-3d, including optional BVH, with focused algorithm comments |
| `src/` | Provided framework and program entry points |
| `external/` | Provided dependency setup |
| `reference/` | Provided comparison images and linear reference |
| `build/` | Existing local build directory |
| `out/` | Runtime output; ignored by Git |
| `docs/` | Notes, consolidated AI records, Markdown report, final LaTeX and PDF |
| `evidence/` | Deliberately retained images, screenshots, terminal text, data and plots |

The 2026-11-05 implementation session built all three programs in Release mode, checked geometry and sampling, and retained default renders, experiment panels, tables, and plots under `evidence/`. Finalization on 2026-11-06 adds the student's name/ID and original prediction responses, a refined report, a 15-entry consolidated AI log, LaTeX, and a rendered PDF. Predictions were supplied after measurements and are identified as a later exercise. Unprovided model labels and student AI-log reasoning/verification are marked as not recorded.

The final report uses a plain A4 LaTeX article with Computer Modern typography, numbered write-ups, figures, tables, terminal panels, and AI-log/terminal appendices. To rebuild it, run `python docs/report/build_report.py` with matplotlib and `pdflatex` available. Graphics paths resolve from `docs/report/latex/`; auxiliary TeX files stay in ignored `build/report-latex/`. Run `docs/report/verify_report.py` with Python's pypdf/pdfplumber packages to check document provenance and integrity. The existing local installations were used without installing packages.

Build with `cmake --build build --config Release`. The existing Visual Studio build places the programs in `build/Release/`. Run `raytrace.exe`, `mesh.exe`, or `pathtrace.exe` there; their default images are saved under `out/`. See the report and evidence index for the exact measured commands and copied-source experiments.

The handout limits submitted source changes to the three student `.cpp` files. These workspace documentation folders are for preparing the report; check the handout before choosing submission contents.
