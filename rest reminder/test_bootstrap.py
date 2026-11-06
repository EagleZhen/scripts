"""Focused setup regressions; no notifications or screen locking."""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import venv
from pathlib import Path
from unittest.mock import patch


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("reminder_launch", Path(__file__).with_name("launch.py"))
        self.launch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.launch)
        self.directory = tempfile.TemporaryDirectory(prefix="rest reminder ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.requirements = self.root / "requirements.txt"
        self.requirements.write_text("", encoding="utf-8")
        self.python = self.launch.environment_python(self.root)
        self.stamp = self.root / ".venv" / ".installed-requirements.txt"

    def test_partial_environment_is_repaired_and_reused(self):
        shutil.copy2(Path(__file__).with_name("launch.py"), self.root / "launch.py")
        # The child reports its interpreter and arguments instead of running a timer.
        (self.root / "rest reminder.py").write_text(
            "import json, sys\nprint(json.dumps([sys.prefix, sys.argv[1:]]))\n", encoding="utf-8"
        )
        venv.EnvBuilder(with_pip=False).create(self.root / ".venv")
        missing_pip = subprocess.run([str(self.python), "-I", "-m", "pip", "--version"], capture_output=True)
        self.assertNotEqual(missing_pip.returncode, 0)

        command = [str(self.python), "-I", str(self.root / "launch.py"), "--interval", "2.5"]
        first = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(self.stamp.exists())
        prefix, arguments = json.loads(first.stdout.splitlines()[-1])
        self.assertEqual(Path(prefix).resolve(), (self.root / ".venv").resolve())
        self.assertEqual(arguments, ["--interval", "2.5"])

        reused = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(reused.returncode, 0, reused.stderr)
        # Reuse produces only the child's output, without running setup again.
        self.assertEqual(json.loads(reused.stdout), [prefix, arguments])

    def test_failed_install_is_retried(self):
        self.python.parent.mkdir(parents=True)
        self.python.touch()

        def fail_install(command, **kwargs):
            if "pip" in command:
                raise subprocess.CalledProcessError(1, command)

        with patch.object(self.launch.subprocess, "run", side_effect=fail_install), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(subprocess.CalledProcessError):
                self.launch.prepare_environment(self.root)
        self.assertFalse(self.stamp.exists())
        with patch.object(self.launch.subprocess, "run") as run, contextlib.redirect_stdout(io.StringIO()):
            self.launch.prepare_environment(self.root)
        self.assertEqual(sum("install" in call.args[0] for call in run.call_args_list), 1)
        self.assertTrue(self.stamp.exists())


@unittest.skipIf(os.name == "nt", "The macOS shell launcher is checked on Unix.")
class MacLauncherTests(unittest.TestCase):
    def test_first_run_resolves_python_from_tool_directory(self):
        with tempfile.TemporaryDirectory(prefix="reminder launcher ") as temporary:
            root = Path(temporary)
            tool = root / "tool with spaces"
            binaries = root / "bin"
            elsewhere = root / "elsewhere"
            for directory in (tool, binaries, elsewhere):
                directory.mkdir()
            launcher = tool / "Start Rest Reminder.command"
            shutil.copy2(Path(__file__).with_name(launcher.name), launcher)
            python = binaries / "python3"
            # Replace only the external interpreter; report where it was resolved.
            python.write_text("#!/bin/sh\npwd\n", encoding="utf-8")
            python.chmod(0o755)
            environment = dict(os.environ, PATH=f"{binaries}:/usr/bin:/bin", PYTHONPATH="/nonexistent")
            result = subprocess.run(
                [str(launcher), "--help"], cwd=elsewhere, env=environment, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(result.stdout.strip()).resolve(), tool.resolve())


if __name__ == "__main__":
    unittest.main()
