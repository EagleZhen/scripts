
try:
    import threading
    import time
    import keyboard
    import pydirectinput
except ImportError:
    print("Missing dependencies. Run: pip install pydirectinput keyboard")
    raise SystemExit(1)

# --- Configure this sequence to match your in-game prompts ---
# Each step: (key_name, hold_seconds, delay_after_seconds)
KEY_SEQUENCE = [
    ("space", 0.08, 0.5),  # tap: "Cook another"
    # ("space", 5.0, 2.0),  # hold: accelerate cooking
    ("r", 0.08, 0.5),      # "Stow"
]

IDLE_SLEEP = 0.05

running = False
exit_event = threading.Event()


def press_key(key: str, hold: float):
    pydirectinput.keyDown(key)
    time.sleep(hold)
    pydirectinput.keyUp(key)


def worker():
    while not exit_event.is_set():
        if running:
            for key, hold, delay in KEY_SEQUENCE:
                if exit_event.is_set() or not running:
                    break
                press_key(key, hold)
                time.sleep(delay)
        else:
            time.sleep(IDLE_SLEEP)


def toggle_running():
    global running
    running = not running
    print("RUNNING" if running else "PAUSED")


def stop_and_exit():
    global running
    running = False
    exit_event.set()
    print("STOPPED")


def main():
    print("F8 = start/pause | F9 = stop & exit")
    print("Switch to RDR2 window after starting.")
    keyboard.add_hotkey("f8", toggle_running)
    keyboard.add_hotkey("f9", stop_and_exit)

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    while not exit_event.is_set():
        time.sleep(0.1)


if __name__ == "__main__":
    main()
