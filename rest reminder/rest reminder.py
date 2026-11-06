"""A rest timer with native notifications and screen locking on macOS and Windows."""

import argparse
import ctypes
import math
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path


LOG_FILE_PATH = Path(__file__).resolve().with_name("log.txt")
BREAK_IMAGE_URL = "https://unsplash.it/3840/2160?random"
GRACE_SECONDS = 30
BREAK_SECONDS = 5 * 60


def print_message(message, log_path):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {message}"
    print(line, flush=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(line + "\n")


def run_applescript(source, *arguments):
    try:
        subprocess.run(
            ["/usr/bin/osascript", "-e", source, *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(error.stderr.strip() or "AppleScript failed") from error


def notify(title, message):
    if sys.platform == "darwin":
        # Pass notification text as data, not interpolated AppleScript source.
        run_applescript(
            "on run argv\n"
            "display notification (item 2 of argv) with title (item 1 of argv)\n"
            "end run",
            title,
            message,
        )
    elif sys.platform == "win32":
        try:
            from win11toast import notify as windows_notify
        except ImportError as error:
            raise RuntimeError("Use Start Rest Reminder.cmd to install the Windows notification dependency.") from error
        windows_notify(title=title, body=message)
    else:
        raise RuntimeError("Rest Reminder supports macOS and Windows.")


def lock_screen():
    if sys.platform == "darwin":
        try:
            run_applescript('tell application "System Events" to keystroke "q" using {control down, command down}')
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            raise RuntimeError(
                "Could not lock the screen. In System Settings > Privacy & Security, "
                "allow your terminal app under Device Control (Accessibility on some macOS versions) "
                "and allow it to control "
                f"System Events under Automation, then restart the reminder. Details: {error}"
            ) from error
    elif sys.platform == "win32":
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.LockWorkStation.argtypes = []
        user32.LockWorkStation.restype = ctypes.c_int
        if not user32.LockWorkStation():
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        raise RuntimeError("Rest Reminder supports macOS and Windows.")


def positive_minutes(value):
    try:
        minutes = float(value)
        if not math.isfinite(minutes) or minutes <= 0:
            raise ValueError
        # Also reject values too large to schedule or represent as seconds.
        datetime.now() + timedelta(minutes=minutes)
    except (ValueError, OverflowError):
        raise argparse.ArgumentTypeError("Enter a finite, positive number of minutes within the supported date range.") from None
    return minutes


def wait(seconds):
    """Count wall-clock time, including laptop sleep, without replaying missed breaks."""
    deadline = time.time() + seconds
    while (remaining := deadline - time.time()) > 0:
        time.sleep(min(remaining, 1))


def reminder(interval_minutes, log_path):
    break_count = 0
    while True:
        break_count += 1
        print(f"\n{'=' * 50}\n")
        next_rest_time = datetime.now() + timedelta(minutes=interval_minutes)
        print_message(f"Break {break_count} is scheduled at {next_rest_time:%m-%d %H:%M:%S}.", log_path)
        wait(interval_minutes * 60)

        print_message("Time to take a break! 🍵", log_path)
        try:
            notify("Rest Reminder", "Time to take a break! 🍵")
        except Exception as error:
            # A notification failure must not prevent the scheduled screen lock.
            print_message(f"Warning: notification failed: {error}", log_path)

        try:
            webbrowser.open_new_tab(BREAK_IMAGE_URL)
        except webbrowser.Error as error:
            print_message(f"Warning: browser could not open: {error}", log_path)
        wait(GRACE_SECONDS)
        print_message("Locking the screen...", log_path)
        lock_screen()
        wait(BREAK_SECONDS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=positive_minutes, metavar="MINUTES", help="Reminder interval; prompts if omitted.")
    parser.add_argument("--test-notification", action="store_true", help="Send one notification and exit without locking the screen.")
    args = parser.parse_args(argv)

    try:
        if sys.platform not in ("darwin", "win32"):
            raise RuntimeError("Rest Reminder supports macOS and Windows.")
        if args.test_notification:
            notify("Rest Reminder", "Test notification: your reminder is ready. 🍵")
            print("Notification requested. Check Notification Center if no banner appears.")
            return 0

        interval = args.interval
        while interval is None:
            try:
                interval = positive_minutes(input("Enter the reminder interval in minutes: "))
            except argparse.ArgumentTypeError as error:
                print(error)

        print(f"Log: {LOG_FILE_PATH}\nPress Ctrl+C to stop.")
        print_message(f"========== Rest reminder started with interval of {interval:g} minutes ==========", LOG_FILE_PATH)
        reminder(interval, LOG_FILE_PATH)
    except (KeyboardInterrupt, EOFError):
        print("\nRest reminder stopped.")
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Rest reminder stopped: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
