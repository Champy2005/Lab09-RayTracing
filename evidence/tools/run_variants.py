"""Build changed student translation units separately; never modify the final student sources."""
import json
from pathlib import Path
import shutil
import subprocess
from msvc_tools import ROOT, compile_cpp
from run_experiments import run


def build_variant(name, changed_file, changes, program):
    variant = ROOT / f"evidence/data/variants/{name}"
    variant.mkdir(parents=True, exist_ok=True)
    for source in (ROOT / "student").glob("*.cpp"):
        shutil.copy2(source, variant / source.name)
    source = variant / changed_file
    text = source.read_text(encoding="utf-8")
    for before, after in changes:
        if text.count(before) != 1:
            raise RuntimeError(f"Expected exactly one replacement in {source}: {before}")
        text = text.replace(before, after)
    source.write_text(text, encoding="utf-8")
    (variant / "changes.json").write_text(json.dumps({"file": changed_file, "changes": changes}, indent=2), encoding="utf-8")
    obj = ROOT / f"build/experiments/{name}/{source.stem}.obj"
    compile_cpp(source, obj, compile_only=True)
    main = next((ROOT / f"build/{program}.dir/Release").rglob(f"{program}_main.obj"))
    executable = ROOT / f"build/experiments/{name}/{program}.exe"
    compiler_env = __import__("msvc_tools").environment()
    linker = Path(r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe")
    command = [str(linker), "/nologo", f"/OUT:{executable}", str(obj), str(main), str(ROOT / "build/Release/lab09core.lib")]
    result = subprocess.run(command, env=compiler_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (ROOT / f"evidence/terminal/link-{name}.txt").write_text(
        subprocess.list2cmdline(command) + "\n\n" + result.stdout.decode(errors="replace") + f"\nExit code: {result.returncode}\n", encoding="utf-8")
    result.check_returncode()
    return executable.relative_to(ROOT).as_posix(), variant


def main():
    exe, variant = build_variant("tir-reflect", "raytracer.cpp", [
        ("    vec3 direction; // refract writes this only if a real transmitted direction exists.",
         "    vec3 direction; transmitted = reflected; // EXPERIMENT: redirect the TIR transmission weight into reflection.")], "raytrace")
    run("P1-tir-reflect", "raytrace", executable=exe, variant=variant)
    exe, variant = build_variant("skip-zero-weights", "raytracer.cpp", [
        ("if(STAGE >= 5) {", "if(STAGE >= 5 && material.albedo[2] > 0.0f) {"),
        ("if(STAGE >= 6) {", "if(STAGE >= 6 && material.albedo[3] > 0.0f) {")], "raytrace")
    run("P1-skip-zero-weights", "raytrace", executable=exe, variant=variant)
    exe, variant = build_variant("cull-backfaces", "mesh.cpp", [
        ("if(std::fabs(determinant) < 1e-8f)", "if(determinant < 1e-8f)")], "mesh")
    run("P2-cull-default", "mesh", executable=exe, variant=variant)
    run("P2-cull-glass", "mesh", ["--glass"], executable=exe, variant=variant)
    exe, variant = build_variant("rr-first-bounce", "pathtracer.cpp", [
        ("if(bounce < 3)", "if(bounce < 0)")], "pathtrace")
    run("P3-rr-first-bounce", "pathtrace", ["--spp", "64"], executable=exe, variant=variant)
    exe, variant = build_variant("shadow-origin-trap", "pathtracer.cpp", [
        ("const vec3 to_light = point - origin;", "const vec3 to_light = point - hit.p;")], "pathtrace")
    run("P3-shadow-origin-trap", "pathtrace", ["--spp", "64"], executable=exe, variant=variant)


if __name__ == "__main__":
    main()
