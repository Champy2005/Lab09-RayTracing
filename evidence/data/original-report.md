# Lab 09: Ray Tracing and Path Tracing

**Intermediate report - student working draft**

All answers, predictions, measurements and interpretations are intentionally left blank. Prompts below paraphrase the lab handout; consult the original for exact wording, equations and figures. No experiments were run to prepare this template.

## 1. Report information

| Field | Value |
| --- | --- |
| Name / student ID | [fill in] |
| Course / section | [fill in] |
| Submission date | [fill in] |
| Repository / branch / revision | [fill in] |
| Draft version / last updated | [fill in] |
| Optional BVH attempted? | [fill in] |

### Machine and reproducibility

| Field | Value |
| --- | --- |
| CPU | [fill in] |
| OS | [fill in] |
| Logical threads / actual threads used | [fill in] |
| Compiler / version | [fill in] |
| CMake / generator | [fill in] |
| Build configuration / relevant flags | [fill in] |
| Timing procedure / repeats | [fill in] |
| Settings kept constant across comparisons | [fill in] |

Full [setup record](../notes/setup.md). Use your own machine's results; sample values printed in the handout are not measurements of your work.

### Sources and related records

- [Original handout](../../instructions-1032980-17933293399497.pdf)
- Chapter 10 source / edition / relevant pages: [not supplied]
- Chapter's Lab 10 Part 1 code source: [not supplied]
- [AI prompt log](../ai/ai-log.md)
- [Evidence index and run-record template](../../evidence/README.md)
- [Extra questions and answers](../notes/questions-and-answers.md)

## 2. Predictions recorded before measurement

Required for write-up 2.1 and write-ups 3.1 and 3.2. Write your own predictions before the relevant run. Preserve the original text after measurement, even when wrong; add your reflection in the later write-up. Record time, timezone, and a saved revision so the sequence is clear.

### Prediction for 2.1: mesh sweep

- Recorded at / timezone: [fill in before running]
- Saved revision / record reference: [fill in]
- First relevant run ID and time (complete afterward): [not run]
- What do I predict for render time versus triangle count? [fill in before running]
- What do I predict for triangle tests per ray versus triangle count? [fill in before running]
- If attempting BVH, what do I predict for its scaling and the median/SAH comparison? [fill in before running, or mark not attempted]
- My reasoning and assumptions: [fill in before running]

### Prediction for 3.1: path-tracing convergence

- Recorded at / timezone: [fill in before running]
- Saved revision / record reference: [fill in]
- First relevant run ID and time (complete afterward): [not run]
- What trend and log-log slope do I predict for RMSE versus spp? [fill in before running]
- What do I predict for RMSE times square root of spp at larger sample counts and with another seed? [fill in before running]
- What sample count and time do I predict for the requested noise reduction? [fill in before running]
- My reasoning and assumptions: [fill in before running]

### Prediction for 3.2: light sampling on/off

- Recorded at / timezone: [fill in before running]
- Saved revision / record reference: [fill in]
- First relevant run ID and time (complete afterward): [not run]
- What visual difference, RMSE and time do I predict at 16 spp? [fill in before running]
- How many samples do I predict no-NEE will need to match default NEE at 16 spp? [fill in before running]
- My reasoning and assumptions: [fill in before running]

## 3. Implementation record (complete later)

Describe your work when it exists; this table does not assign implementation to an AI agent.

| Task | File / functions | My explanation / revision | Verification evidence |
| --- | --- | --- | --- |
| 1a | `student/raytracer.cpp`: `camera_ray` | [fill in] | [fill in] |
| 1b | `student/raytracer.cpp`: `ray_sphere` | [fill in] | [fill in] |
| 1c | `student/raytracer.cpp`: `reflect`, `refract` | [fill in] | [fill in] |
| 1d | `student/raytracer.cpp`: `cast_ray` | [fill in] | [fill in] |
| 2a | `student/mesh.cpp`: `ray_triangle` | [fill in] | [fill in] |
| 2b | `student/mesh.cpp`: `intersect_mesh` | [fill in] | [fill in] |
| 2c, optional | `student/mesh.cpp`: `ray_aabb` | [fill in] | [fill in] |
| 2d, optional | `student/mesh.cpp`: `intersect_bvh` | [fill in] | [fill in] |
| 3a | `student/pathtracer.cpp`: `cosine_sample_hemisphere` | [fill in] | [fill in] |
| 3b | `student/pathtracer.cpp`: `sample_light` | [fill in] | [fill in] |
| 3c | `student/pathtracer.cpp`: `russian_roulette` | [fill in] | [fill in] |
| 3d | `student/pathtracer.cpp`: `path_trace` | [fill in] | [fill in] |

## 4. Required default renders and panels

Keep the actual command, configuration, image, panel and revision together in the evidence index. Inspect existing outputs before deciding whether they represent a suitable baseline.

| Program | Exact command / run ID | Image evidence | Panel evidence | My comparison with supplied reference |
| --- | --- | --- | --- | --- |
| `raytrace`, default flags | [not run] | [fill in] | [fill in] | [fill in] |
| `mesh`, default flags | [not run] | [fill in] | [fill in] | [fill in] |
| `pathtrace`, default flags | [not run] | [fill in] | [fill in] | [fill in] |

Image captions / settings / notable differences: [fill in]

<!-- Enable actual embeds after evidence exists, e.g.:
![Figure 1: your caption](../../evidence/images/part-1/your-file.png)
-->

## 5. Write-up 1: tiny ray tracer

### 1.1: ray-sphere worked examples

Run `--probe` later. What does your code report for the ray from `(0, 0, 0)` toward `(0, 0, -1)` and sphere at `(0, 0, -5)`, radius 1? Redo the chapter's calculation using handout Equation 3, locate the slip, and give both roots. Repeat for the ray starting at `(0, 0, 3)`.

| Origin | My coefficients / discriminant | Both hand-calculated roots | Probe output | Evidence |
| --- | --- | --- | --- | --- |
| `(0, 0, 0)` | [fill in] | [fill in] | [not run] | [fill in] |
| `(0, 0, 3)` | [fill in] | [fill in] | [not run] | [fill in] |

My calculation, correction and explanation: [fill in]

### 1.2: zero EPS and scene scale

Compare `--eps 0` with the default. Explain the observed artifacts at floating-point level: where does a shadow ray begin and what does it hit first? Read the floor intersection in `scene.cpp`: why does its behavior differ? If every scene coordinate were multiplied by 1000 to use millimetres, what would EPS `0.001` do?

- Commands / revisions / evidence for both cases: [fill in]
- Image(s) and captions: [fill in]
- My observations: [fill in]
- My explanation, including the floor code reference and units: [fill in]

### 1.3: depth, ray counts and time

Measure `--depth 0, 1, 2, 3, 4`. Compare the ray-count growth with the chapter's ray tree. Explain which rays your implementation casts at each hit, what happens when a ray leaves the scene, and whether it casts reflection/refraction rays with zero weights. Which rays could be skipped without changing pixels, and what would be saved?

| Depth | Time (ms) | Rays / pixel | Threads / revision / run ID | Evidence |
| --- | --- | --- | --- | --- |
| 0 | [not run] | [not run] | [fill in] | [fill in] |
| 1 | [not run] | [not run] | [fill in] | [fill in] |
| 2 | [not run] | [not run] | [fill in] | [fill in] |
| 3 | [not run] | [not run] | [fill in] | [fill in] |
| 4 | [not run] | [not run] | [fill in] | [fill in] |

My explanation and calculation of potential savings: [fill in]

### 1.4: glass wedge and a one-line change

Make the dark wedge disappear and reappear with one line changed. What does Equation 4 say about it? Where does that light physically go, and what does this implementation do instead?

- Original line / changed line / revision / restoration record: [fill in]
- Before and after commands / images / panels: [fill in]
- My explanation and equation reference: [fill in]

### Part I supporting stages

Keep evidence for the six lesson stages when implemented later.

| Stage | Run / settings | Image / panel evidence | My observations |
| --- | --- | --- | --- |
| 1 | [not run] | [fill in] | [fill in] |
| 2 | [not run] | [fill in] | [fill in] |
| 3 | [not run] | [fill in] | [fill in] |
| 4 | [not run] | [fill in] | [fill in] |
| 5 | [not run] | [fill in] | [fill in] |
| 6 | [not run] | [fill in] | [fill in] |

## 6. Write-up 2: triangles

### 2.1: sweep, scaling and extrapolation

Complete the prediction in section 2 before running `--sweep`. Present tables and log-log plots of render time and triangle tests per ray versus N; fit their slopes. Compute the fraction of rays reaching the knot's bounding sphere. Extrapolate brute force, and BVH if attempted, to 10 million triangles. Evaluate the chapter's operations-per-ray and under-5-ms claims using your measurements, including the 16k knot at both 320 x 240 and 800 x 600.

| Nominal size | Actual N | Method | Build (ms) | Render (ms) | Tests / ray | Nodes / ray | Run / evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |
| 2k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |
| 4k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |
| 16k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |
| 64k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |
| 256k | [fill in] | [fill in] | [not run] | [not run] | [not run] | [not run] | [fill in] |

Add separate rows for each tested method. Distinguish measured, skipped and extrapolated values; do not fill skipped rows with apparent measurements.

- Raw sweep / exact settings / evidence: [fill in]
- Plot of render time versus N and caption: [fill in]
- Plot of triangle tests per ray versus N and caption: [fill in]
- Fitting method, fitted slopes and included points: [fill in]
- Fraction of rays reaching the bounding sphere, with calculation: [fill in]
- 10-million-triangle extrapolation and assumptions: [fill in]

| 16k comparison | Method | Measured time / extrapolated estimate (label which) | Comparison to 5 ms | Evidence / calculation |
| --- | --- | --- | --- | --- |
| 320 x 240 | [fill in] | [fill in] | [fill in] | [fill in] |
| 800 x 600 | [fill in] | [fill in] | [fill in] | [fill in] |

- My interpretation of the chapter's claims: [fill in]
- Reflection on my original prediction, without changing it: [fill in]

### 2.2: flat versus interpolated normals

Compare the default render with `--flat`. Why are u and v available without extra intersection work in Equation 6? What else could be interpolated with them?

- Commands / images / panels: [fill in]
- My observations and explanation: [fill in]
- Other interpolated attributes: [fill in]

### 2.3: back-face culling

Compare the absolute-determinant rejection test with its signed version, as specified in the handout. Render the default knot and glass knot both ways. What changes and why? Which direction do the knot's triangles face? Under what conditions could a GPU cull triangles of a glass object?

| Material | Culling setting / exact code revision | Command | Image / panel | My observations |
| --- | --- | --- | --- | --- |
| Default | [fill in] | [not run] | [fill in] | [fill in] |
| Default | [fill in] | [not run] | [fill in] | [fill in] |
| Glass | [fill in] | [not run] | [fill in] | [fill in] |
| Glass | [fill in] | [not run] | [fill in] | [fill in] |

- Original / modified line and restoration record: [fill in]
- My explanation and GPU discussion: [fill in]

### 2.4: optional BVH comparison

- Attempted / not attempted: [fill in]

If attempted, compare median and SAH using build time, nodes per ray, triangle tests per ray and render time. Explain the tradeoff using Equation 10.05 and the builder's cost constants. Which wins on your machine, and by how much?

- Linked sweep rows / plots / evidence: [fill in]
- My cost analysis and explanation: [fill in]
- Measured winner / size of difference / limits: [fill in]

## 7. Write-up 3: path tracer

### 3.1: convergence, seeds and reference noise

Complete the prediction in section 2 first. Run the sample sweep with the default seed and seed 1. Include its table and a log-log plot of RMSE versus spp. Compare the fitted slope with the handout's expected slope. Explain the behavior of RMSE times square root of spp at 256 samples using how the reference was made. Estimate samples and runtime for an image 10 times less noisy than at 16 spp, and compare with the chapter's sampling claim.

| Seed | spp | Time (ms) | RMSE | RMSE times sqrt(spp) | Run / evidence |
| --- | --- | --- | --- | --- | --- |
| 0 | 1 | [not run] | [not run] | [not run] | [fill in] |
| 0 | 4 | [not run] | [not run] | [not run] | [fill in] |
| 0 | 16 | [not run] | [not run] | [not run] | [fill in] |
| 0 | 64 | [not run] | [not run] | [not run] | [fill in] |
| 0 | 256 | [not run] | [not run] | [not run] | [fill in] |
| 1 | 1 | [not run] | [not run] | [not run] | [fill in] |
| 1 | 4 | [not run] | [not run] | [not run] | [fill in] |
| 1 | 16 | [not run] | [not run] | [not run] | [fill in] |
| 1 | 64 | [not run] | [not run] | [not run] | [fill in] |
| 1 | 256 | [not run] | [not run] | [not run] | [fill in] |

- Plot / fit method / slopes / evidence: [fill in]
- My reference-noise and seed analysis: [fill in]
- My sample-count and runtime calculation, with units and assumptions: [fill in]
- Reflection on my original prediction: [fill in]

### 3.2: next event estimation

Complete the prediction in section 2 first. Compare default and `--no-nee` at 16 spp using images, RMSE and time. Find how many no-NEE samples are needed to match NEE at 16 spp. Estimate the fraction of cosine-weighted directions from the middle of the floor that reach the lamp and use it to explain the gap.

| Configuration | spp | Seed / controlled settings | RMSE | Time (ms) | Image / panel / run |
| --- | --- | --- | --- | --- | --- |
| NEE on | 16 | [fill in] | [not run] | [not run] | [fill in] |
| NEE off | 16 | [fill in] | [not run] | [not run] | [fill in] |
| NEE off, matched error | [fill in] | [fill in] | [not run] | [not run] | [fill in] |

- My matching criterion and any additional runs: [fill in]
- My lamp-fraction estimate and derivation: [fill in]
- My image comparison and explanation: [fill in]
- Reflection on my original prediction: [fill in]

### 3.3: Russian roulette and the chapter code

At 64 spp compare default and `--no-rr`: mean, RMSE, runtime and rays per sample. Is the estimator unbiased, and is the noise/time tradeoff worthwhile? Compare efficiency `1 / (RMSE^2 * time)` using consistent time units.

| Configuration | Mean | RMSE | Time (ms) | Rays / sample | Efficiency / units | Run / evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Default RR, 64 spp | [not run] | [not run] | [not run] | [not run] | [fill in] | [fill in] |
| No RR, 64 spp | [not run] | [not run] | [not run] | [not run] | [fill in] | [fill in] |
| My code variant, 64 spp | [not run] | [not run] | [not run] | [not run] | [fill in] | [fill in] |

- My bias and efficiency analysis, including limits of the evidence: [fill in]

Read the chapter's Lab 10 Part 1 CPU path-tracer code. What is missing from `Hit` for it to compile? Can its post-roulette emissive return produce 12? It chooses q from current albedo rather than accumulated throughput and starts roulette at the first bounce: which issues affect correctness, noise or runtime? Measure at least one through a code change.

- Chapter source / page / code reference: [not supplied]
- My answers about `Hit` and the emissive return: [fill in]
- My classification of the roulette choices and reasoning: [fill in]
- Chosen change / original and modified code / revision / restoration: [fill in]
- Measurement, evidence and interpretation of that change: [fill in]

### 3.4: depth and missing light

At 64 spp measure depths 1, 2, 3, 5 and 10, and compare their means with the reference. How much does each added depth contribute? How much light is lost with the chapter's hard cut at 10? Explain the comparison with roulette at depth 64 even though most paths stop earlier.

| Depth / configuration | Mean | Reference mean | Difference / light contribution (define measure) | Run / evidence |
| --- | --- | --- | --- | --- |
| 1, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |
| 2, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |
| 3, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |
| 5, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |
| 10, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |
| RR on, depth 64, 64 spp | [not run] | [fill in] | [fill in] | [fill in] |

- Images / captions / exact settings: [fill in]
- My calculations and explanation: [fill in]

### 3.5: reintroduce one of the two traps

Choose one of the traps described for TASK 3b or 3d. Reintroduce it later, compare means and images with and without it, and explain the mean change using Equation 12.

- Chosen trap and why I chose it: [fill in]
- Original / changed line(s), code revision and restoration record: [fill in]

| Variant | Exact command / controlled settings | Mean | Image / panel / run |
| --- | --- | --- | --- |
| Without the trap | [not run] | [not run] | [fill in] |
| With the trap | [not run] | [not run] | [fill in] |

- My explanation using Equation 12: [fill in]

## 8. Discussion and learning record

- Which measurements surprised me, and what evidence explains them? [fill in]
- Which differences from the chapter can I justify? [fill in]
- What remains uncertain or unverified? [fill in]
- What can I explain and predict for a live one-line code change? [fill in]
- What did each agent contribute, and how did I evaluate those suggestions? [fill in; link prompt IDs]

## 9. References and evidence captions

| ID | Source / title | Author / edition / date | Page / equation / URL or local path | Used in section |
| --- | --- | --- | --- | --- |
| [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |

| Figure / table ID | Evidence ID / file | Caption | Settings / revision / origin |
| --- | --- | --- | --- |
| [fill in] | [fill in] | [fill in] | [fill in] |

## 10. Before later LaTeX and PDF finalization

- [ ] My identity, CPU, thread count and compiler are recorded.
- [ ] Required predictions were saved before measurements and remain unchanged.
- [ ] Default images and terminal panels for all three programs are included.
- [ ] Every required write-up question is answered from my own evidence.
- [ ] Optional BVH work is clearly marked attempted or not attempted.
- [ ] Requested plots, fitted slopes, calculations, units and settings are present.
- [ ] Temporary code experiments and their restoration are documented.
- [ ] Every prompt to either agent has an AI-log entry with my idea and verification.
- [ ] Sources, image captions and evidence paths are complete.
- [ ] I can explain the submitted code and predict a live change.
- [ ] Submission contents match the handout's source-change restrictions.
- [ ] Markdown content is ready for later conversion to `latex/`.
- [ ] After conversion is requested, render and visually review the PDF before placing it in `final/`.

LaTeX conversion and PDF rendering are deferred. These boxes are placeholders, not completed checks.
