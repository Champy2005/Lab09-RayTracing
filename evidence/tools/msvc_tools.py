"""Use the already installed Visual Studio toolchain for isolated validation builds."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def environment():
    setup = Path(r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat")
    result = subprocess.run(f'cmd.exe /d /s /c ""{setup}" >nul && set"',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    values = {key.upper(): value for key, value in os.environ.items()}
    for line in result.stdout.decode("utf-8", errors="replace").splitlines():
        if "=" in line and not line.startswith("="):
            key, value = line.split("=", 1)
            values[key.upper()] = value
    return values


def compile_cpp(source, output, objects=(), compile_only=False):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    compiler = Path(r"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe")
    command = [str(compiler), "/nologo", "/std:c++17", "/O2", "/EHsc", "/MD", "/W4", "/permissive-",
               "/DNDEBUG", "/D_CRT_SECURE_NO_WARNINGS", f'/DLAB09_ROOT="{ROOT.as_posix()}"',
               f"/I{ROOT / 'student'}", f"/I{ROOT / 'src'}", str(source), f"/Fo{output.with_suffix('.obj')}"]
    command += ["/c"] if compile_only else [f"/Fe{output}", *(str(p) for p in objects)]
    result = subprocess.run(command, env=environment(), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = result.stdout.decode("utf-8", errors="replace")
    (ROOT / f"evidence/terminal/build-{output.parent.name}-{output.stem}.txt").write_text(
        subprocess.list2cmdline(command) + "\n\n" + text + f"\nExit code: {result.returncode}\n", encoding="utf-8")
    print(text, flush=True)
    result.check_returncode()


if __name__ == "__main__":
    executable = ROOT / "build/validation/verify.exe"
    compile_cpp(ROOT / "evidence/tools/verify.cpp", executable, [ROOT / "build/Release/lab09core.lib"])
    result = subprocess.run([str(executable)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = result.stdout.decode("utf-8", errors="replace")
    (ROOT / "evidence/terminal/verification.txt").write_text(text + f"\nExit code: {result.returncode}\n", encoding="utf-8")
    print(text, flush=True)
    result.check_returncode()
