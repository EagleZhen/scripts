"""Create/reuse this tool's virtual environment, then run the reminder."""

import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def environment_python(directory):
    environment = directory / ".venv"
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def prepare_environment(directory):
    environment = directory / ".venv"
    python = environment_python(directory)
    if not python.is_file():
        print("Creating the reminder's Python environment...", flush=True)
        venv.EnvBuilder(with_pip=False).create(environment)

    requirements = directory / "requirements.txt"
    requested = requirements.read_text(encoding="utf-8")
    installed = environment / ".installed-requirements.txt"
    if not installed.exists() or installed.read_text(encoding="utf-8") != requested:
        print("Setting up reminder dependencies...", flush=True)
        # Seed pip separately so an interrupted first setup can repair itself.
        subprocess.run([str(python), "-I", "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run(
            [
                str(python), "-I", "-m", "pip", "--isolated", "install",
                "--disable-pip-version-check", "--require-virtualenv", "-r", str(requirements),
            ],
            check=True,
        )
        # Write this only after a successful install so failures are retryable.
        installed.write_text(requested, encoding="utf-8")
    return python


def main(argv=None):
    try:
        python = prepare_environment(ROOT)
        return subprocess.run(
            [str(python), "-X", "utf8", "-I", str(ROOT / "rest reminder.py"), *(sys.argv[1:] if argv is None else argv)],
            cwd=ROOT,
        ).returncode
    except KeyboardInterrupt:
        return 0
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Could not start Rest Reminder: {error}", file=sys.stderr)
        print("Check the error above and retry. For a broken or moved environment, remove only rest reminder/.venv and launch again.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
