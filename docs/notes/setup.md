# Setup record

Record work you have already done before planning anything new. All verification fields are intentionally blank.

## Personal and machine information

| Field | Your record |
| --- | --- |
| Name / student ID | [fill in] |
| Course / section | [fill in] |
| OS and version | [fill in] |
| CPU | [fill in] |
| Physical cores / logical threads | [fill in] |
| Compiler and version | [fill in] |
| CMake version | [fill in] |
| Generator / toolchain | [fill in] |
| Build configuration | [fill in] |
| Actual threads used for experiments | [fill in] |
| Repository / branch / revision | [fill in] |

## Existing work to document

Observed during scaffolding: `build/`, `out/raytrace.png`, `.vscode/c_cpp_properties.json`, `.clangd`, and `compile_commands.json` exist. Their presence does not establish that the current project builds or renders correctly. No setup verification was run as part of this scaffold.

| Step already attempted | Exact command or action | Date / revision | Outcome in your words | Evidence |
| --- | --- | --- | --- | --- |
| [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |

## Checklist for later verification

- [ ] Record the existing compiler, CMake and editor setup.
- [ ] Check the handout's C++17 and CMake 3.16+ requirements.
- [ ] Record dependency availability and any first-build download.
- [ ] Record configure/build commands and their actual outcomes.
- [ ] Record the executable locations for this generator/configuration.
- [ ] Save the baseline panel and image for each program when appropriate.
- [ ] Record any warnings or unresolved setup issues.

## Planned steps, not executed

| Proposed action / command | Why needed | When to run | Outcome / evidence after execution |
| --- | --- | --- | --- |
| [fill in] | [fill in] | [fill in] | [not run] |

## Questions about setup

- What have I already completed? [fill in]
- What remains uncertain? [fill in]
- Which setup changes, if any, do I want help with next? [fill in]

## Assistant-run implementation verification, 2026-11-05

This dated record follows the original scaffold above. It records actual assistant execution, not the student's personal setup claims.

| Item | Observed result |
| --- | --- |
| CPU / cores / threads | Intel Core Ultra 9 275HX; 24 physical cores, 24 logical threads |
| OS | Windows 11 Home Single Language, 10.0.26200 |
| Compiler | MSVC 19.51.36257.0, x64 |
| CMake / generator | 4.3.1-msvc1; Visual Studio 18 2026, x64 |
| Command actually executed | cmake --build build --config Release |
| Result | All three programs built; no compiler warnings in retained output |
| Executables | build/Release/raytrace.exe, mesh.exe, pathtrace.exe |
| Experiments | 24 threads; exact commands, timestamps, source hashes, and panels in the evidence manifest |
| Dependency changes | None installed; supplied stb header and existing toolchains used |
| Plotting | Existing Python/matplotlib installation; separate from renderer requirements |
| Independent checks | 115912 passing checks; details in verification log |

[Build log](../../evidence/terminal/build-release.txt), [verification](../../evidence/terminal/verification.txt), [machine and source manifest](../../evidence/data/session-manifest.json), [all run records](../../evidence/data/runs.jsonl).

Personal setup/verification fields in the original template are still for the student to complete.
