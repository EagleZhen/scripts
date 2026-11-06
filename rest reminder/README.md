# Rest Reminder

Sends a notification and opens a random image after your chosen interval, waits 30 seconds, locks the screen, then waits five minutes before starting the next interval.

Install Python 3, then double-click the launcher:

- **macOS:** `Start Rest Reminder.command`
- **Windows:** `Start Rest Reminder.cmd` (Python must be available through `py` or `python`).

First launch creates a local `.venv` and installs this tool's `requirements.txt`. Windows needs internet access for its notification package; macOS uses built-in AppleScript. No activation, global packages, or `PYTHONPATH` setup is required.

## macOS permissions

In **System Settings > Privacy & Security**, enable **Terminal** under **Device Control** (called **Accessibility** on some macOS versions). Under **Automation > Terminal**, allow **System Events**. If you use another terminal app, grant that app the permissions instead.

## Running and stopping

Keep the terminal open; press **Ctrl+C** or close its window to stop. Logs go to `log.txt` beside the script. Intervals include laptop sleep; an overdue reminder runs once after waking. After moving this folder or replacing its base Python, delete only `.venv` and launch again.

From the repository root, these macOS commands send a test notification or start a short cycle. The second locks the screen after about 33 seconds:

```sh
"./rest reminder/Start Rest Reminder.command" --test-notification
"./rest reminder/Start Rest Reminder.command" --interval 0.05
```

On Windows, pass the same options to `"Start Rest Reminder.cmd"` from this folder.

Run the regression tests from the repository root with `python3 -m unittest discover -s "rest reminder" -p "test_*.py"` (use `py -3` on Windows). Tests never send notifications or lock the screen.
