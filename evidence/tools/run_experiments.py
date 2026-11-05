"""Run the lab executables sequentially and retain their exact commands and results."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BANGKOK = timezone(timedelta(hours=7))
MANIFEST = ROOT / "evidence/data/runs.jsonl"


def source_hashes():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "student").glob("*.cpp"))}


def run(run_id, program, arguments=(), default=False, executable=None, variant=None):
    folder = {"raytrace": "part-1", "mesh": "part-2", "pathtrace": "part-3"}[program]
    image = ROOT / f"evidence/images/{folder}/{run_id}.png"
    args = list(arguments)
    if not default and "--sweep" not in args and "--probe" not in args:
        args += ["--out", image.relative_to(ROOT).as_posix()]
    command = [executable or f"build/Release/{program}.exe", *args]
    started = datetime.now(BANGKOK).isoformat(timespec="seconds")
    print(f"RUN {run_id}: {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = completed.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    log = ROOT / f"evidence/terminal/{run_id}.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(f"Run: {run_id}\nStarted: {started}\nWorking directory: {ROOT}\nCommand: {' '.join(command)}\n\n"
                   + output + f"\nExit code: {completed.returncode}\n", encoding="utf-8")
    if default and completed.returncode == 0:
        image.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f"out/{program}.png", image)
    record = {"id": run_id, "started": started, "finished": datetime.now(BANGKOK).isoformat(timespec="seconds"),
              "command": command, "exit_code": completed.returncode, "source_sha256": source_hashes(),
              "log": log.relative_to(ROOT).as_posix(), "output": output}
    if variant:
        record["variant"] = variant.relative_to(ROOT).as_posix()
        record["source_sha256"] = {f"student/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(variant.glob("*.cpp"))}
    if image.exists():
        record["image"] = image.relative_to(ROOT).as_posix()
        record["image_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
    with MANIFEST.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record) + "\n")
    print(output.strip(), flush=True)
    if completed.returncode or "not done" in output or "FAILED" in output:
        raise RuntimeError(f"Run {run_id} failed; inspect {log}")
    return record


def baseline():
    backup = ROOT / "evidence/data/original-out"
    backup.mkdir(parents=True, exist_ok=True)
    for p in (ROOT / "out").glob("*"):
        if p.is_file() and not (backup / p.name).exists():
            shutil.copy2(p, backup / p.name)
    run("P1-probe", "raytrace", ["--probe"])
    for part, program in enumerate(("raytrace", "mesh", "pathtrace"), 1):
        run(f"P{part}-default", program, default=True)


def experiments():
    for depth in range(5):
        run(f"P1-depth-{depth}", "raytrace", ["--depth", str(depth)])
    run("P1-eps-zero", "raytrace", ["--eps", "0"])
    for stage in range(1, 7):
        run(f"P1-stage-{stage}", "raytrace", ["--stage", str(stage)])
    for setting in ("flat", "glass", "bvh"):
        run(f"P2-{setting}", "mesh", [f"--{setting}"])
    run("P2-median", "mesh", ["--bvh", "--split", "median"])
    for repeat in range(1, 4):
        run(f"P2-sweep-{repeat}", "mesh", ["--sweep"])
    for seed in (0, 1):
        run(f"P3-sweep-seed-{seed}", "pathtrace", ["--sweep", "--seed", str(seed)])
    run("P3-spp-64", "pathtrace", ["--spp", "64"])
    run("P3-no-rr-64", "pathtrace", ["--spp", "64", "--no-rr"])
    for depth in (1, 2, 3, 5, 10):
        run(f"P3-depth-{depth}", "pathtrace", ["--spp", "64", "--depth", str(depth)])
    for spp in (16, 256, 1024):
        run(f"P3-no-nee-{spp}", "pathtrace", ["--no-nee", "--spp", str(spp)])
    run("P3-spp-256", "pathtrace", ["--spp", "256"])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    {"baseline": baseline, "experiments": experiments}[mode]()
