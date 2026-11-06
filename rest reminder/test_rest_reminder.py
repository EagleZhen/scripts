"""Regression tests that do not send notifications or lock the screen."""

import importlib.util
import argparse
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).with_name("rest reminder.py")


def load_reminder():
    spec = importlib.util.spec_from_file_location("rest_reminder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImportTests(unittest.TestCase):
    def test_import_needs_no_global_packages_or_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-I", "-c", "import runpy, sys; runpy.run_path(sys.argv[1])", str(SCRIPT)],
                cwd=directory,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])


class ReminderTests(unittest.TestCase):
    def setUp(self):
        self.reminder = load_reminder()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.log_path = Path(self.directory.name) / "log.txt"
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def test_interval_must_be_positive_and_finite(self):
        for value in ("0", "-1", "nan", "inf", "-inf", "nonsense", "1e308"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                self.reminder.positive_minutes(value)
        self.assertEqual(self.reminder.positive_minutes("0.5"), 0.5)

    def test_wait_counts_time_spent_asleep(self):
        # A laptop sleeps during the first one-second polling sleep.
        with patch.object(self.reminder.time, "time", side_effect=[100, 100, 3700]), patch.object(
            self.reminder.time, "sleep"
        ) as sleep:
            self.reminder.wait(60)
        sleep.assert_called_once_with(1)

    def run_one_cycle(self, notification_error=None):
        events = []
        wait_count = 0

        def wait(seconds):
            nonlocal wait_count
            wait_count += 1
            events.append(("wait", seconds))
            # Stop when the next interval starts, after one complete break.
            if wait_count == 4:
                raise KeyboardInterrupt

        def notify(*args):
            events.append("notify")
            if notification_error:
                raise notification_error

        with patch.object(self.reminder, "wait", side_effect=wait), patch.object(
            self.reminder, "notify", side_effect=notify
        ), patch.object(self.reminder.webbrowser, "open_new_tab", side_effect=lambda url: events.append("browser")), patch.object(
            self.reminder, "lock_screen", side_effect=lambda: events.append("lock")
        ), self.assertRaises(KeyboardInterrupt):
            self.reminder.reminder(2, self.log_path)
        return events

    def test_preserves_reminder_sequence(self):
        for error in (None, RuntimeError("Notifications unavailable")):
            with self.subTest(notification_error=error):
                self.assertEqual(
                    self.run_one_cycle(error),
                    [("wait", 120), "notify", "browser", ("wait", 30), "lock", ("wait", 300), ("wait", 120)],
                )
                if error:
                    self.assertIn(str(error), self.log_path.read_text(encoding="utf-8"))

    def test_macos_lock_failure_explains_permissions(self):
        error = subprocess.CalledProcessError(1, ["osascript"], stderr="Not authorized")
        with patch.object(self.reminder.sys, "platform", "darwin"), patch.object(
            self.reminder.subprocess, "run", side_effect=error
        ), self.assertRaisesRegex(RuntimeError, "Accessibility"):
            self.reminder.lock_screen()

    def test_windows_lock_checks_api_failure(self):
        user32 = Mock()
        user32.LockWorkStation.return_value = 0
        with patch.object(self.reminder.sys, "platform", "win32"), patch.object(
            self.reminder.ctypes, "WinDLL", return_value=user32, create=True
        ), patch.object(self.reminder.ctypes, "get_last_error", return_value=5, create=True), patch.object(
            self.reminder.ctypes, "WinError", return_value=OSError("Lock failed"), create=True
        ) as win_error:
            with self.assertRaises(OSError):
                self.reminder.lock_screen()
        win_error.assert_called_once_with(5)

if __name__ == "__main__":
    unittest.main()
