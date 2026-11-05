"""Derive the report's tables, fits, and plots from retained program output."""
import csv
import json
from pathlib import Path
import re
import statistics
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "evidence/data"
PLOTS = ROOT / "evidence/plots"
runs = [json.loads(line) for line in (DATA / "runs.jsonl").read_text().splitlines()]
by_id = {run["id"]: run for run in runs}
rows = []
for run in runs:
    row = {"id": run["id"], "started": run["started"], "command": " ".join(run["command"])}
    for key, label in (("ms", "time"), ("rays_per_pixel", "rays / pixel"), ("rays_per_sample", "rays / sample"),
                       ("mean", "mean"), ("rmse", "RMSE")):
        match = re.search(r"(?m)^\s*" + re.escape(label) + r"\s+([0-9.]+)", run["output"])
        if match:
            row[key] = float(match[1])
    rows.append(row)
with (DATA / "render-results.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=["id", "started", "command", "ms", "rays_per_pixel", "rays_per_sample", "mean", "rmse"])
    writer.writeheader(); writer.writerows(rows)

sweep_rows = []
for repeat in range(1, 4):
    output = by_id[f"P2-sweep-{repeat}"]["output"]
    pattern = r"(?m)^\s*(\d+)\s+(brute force|bvh median|bvh sah)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$"
    for match in re.finditer(pattern, output):
        n, method, build, ms, tests, nodes = match.groups()
        sweep_rows.append(dict(repeat=repeat, n=int(n), method=method, build_ms=float(build), render_ms=float(ms),
                               tests_per_ray=float(tests), nodes_per_ray=float(nodes)))
with (DATA / "mesh-sweep-raw.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(sweep_rows[0])); writer.writeheader(); writer.writerows(sweep_rows)
medians = []
for n in sorted({r["n"] for r in sweep_rows}):
    for method in ("brute force", "bvh median", "bvh sah"):
        selected = [r for r in sweep_rows if r["n"] == n and r["method"] == method]
        if selected:
            medians.append({"n": n, "method": method, **{key: statistics.median(r[key] for r in selected)
                            for key in ("build_ms", "render_ms", "tests_per_ray", "nodes_per_ray")}})
with (DATA / "mesh-sweep-medians.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(medians[0])); writer.writeheader(); writer.writerows(medians)

fits = {}
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
for method, colour in zip(("brute force", "bvh median", "bvh sah"), ("#b45309", "#2563eb", "#059669")):
    selected = [r for r in medians if r["method"] == method]
    x = np.array([r["n"] for r in selected], float)
    fits[method] = {}
    for ax, key, ylabel in zip(axes, ("render_ms", "tests_per_ray"), ("Render time (ms)", "Triangle tests per primary ray")):
        y = np.array([r[key] for r in selected])
        slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
        fits[method][key] = {"slope": float(slope), "intercept": float(intercept)}
        ax.loglog(x, y, "o-", color=colour, label=f"{method}; slope {slope:.3f}")
        ax.set(xlabel="Actual triangle count N", ylabel=ylabel)
        ax.grid(True, which="both", alpha=0.17)
        ax.legend(fontsize=9)
    if method == "brute force":
        fit = fits[method]["render_ms"]
        estimate = float(np.exp(fit["intercept"]) * 1e7 ** fit["slope"])
    else:
        slope, intercept = np.polyfit(np.log2(x), np.array([r["render_ms"] for r in selected]), 1)
        estimate = float(intercept + slope * np.log2(1e7))
        fits[method]["log_time_fit"] = {"intercept_ms": float(intercept), "ms_per_doubling": float(slope)}
    fits[method]["estimated_render_ms_at_10M_320x240"] = estimate
fig.suptitle("Mesh scaling: median of three sequential Release sweeps, 24 threads")
fig.savefig(PLOTS / "mesh-scaling.png"); plt.close(fig)

path_rows = []
fig, ax = plt.subplots(figsize=(7.5, 4.8), layout="constrained")
for seed, colour in ((0, "#2563eb"), (1, "#b45309")):
    points = []
    output = by_id[f"P3-sweep-seed-{seed}"]["output"]
    for match in re.finditer(r"(?m)^\s*(1|4|16|64|256)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", output):
        n, ms, rmse, scaled = match.groups()
        row = dict(seed=seed, spp=int(n), ms=float(ms), rmse=float(rmse), rmse_sqrt_spp=float(scaled))
        path_rows.append(row); points.append(row)
    x = np.array([r["spp"] for r in points], float); y = np.array([r["rmse"] for r in points])
    # The renderer fits unrounded errors; retain its printed slope rather than fitting rounded errors for the report.
    slope = float(re.search(r"slope\s+(-?[\d.]+)", output).group(1))
    fits[f"path_seed_{seed}"] = {"renderer_log_slope": slope}
    ax.loglog(x, y, "o-", color=colour, label=f"Seed {seed}, fitted slope {slope:.3f}")
ax.loglog(x, 0.082 / np.sqrt(x), "--", color="#6b7280", label="Guide: slope -0.5")
ax.set(xlabel="Samples per pixel", ylabel="Masked linear-RGB RMSE", title="Path-tracer convergence, NEE and roulette enabled")
ax.grid(True, which="both", alpha=0.17); ax.legend()
fig.savefig(PLOTS / "path-convergence.png"); plt.close(fig)
with (DATA / "path-sweeps.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(path_rows[0])); writer.writeheader(); writer.writerows(path_rows)
(DATA / "fits.json").write_text(json.dumps(fits, indent=2))
print(json.dumps(fits, indent=2))

# A simple unoccluded floor-to-lamp solid-angle estimate using Equation 12 with rho*Le removed.
corner = np.array([343., 554., 332.]); floor = np.array([278., 0., 278.])
lamp_midpoint = corner + np.array([-65., 0., -52.5])
delta = lamp_midpoint - floor
d2 = float(delta @ delta); cosine = float(delta[1] / np.sqrt(d2))
p = cosine * cosine * (130 * 105) / (np.pi * d2)
print(f"Unoccluded midpoint lamp-direction fraction: {p:.8f} ({100*p:.4f}%)")
