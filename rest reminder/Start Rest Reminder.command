#!/bin/bash

script_dir="$(cd -- "$(dirname -- "$0")" && pwd)" || exit 1
cd -- "$script_dir" || exit 1

if [ -x "$script_dir/.venv/bin/python" ]; then
    "$script_dir/.venv/bin/python" -X utf8 -I "$script_dir/launch.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    python3 -X utf8 -I "$script_dir/launch.py" "$@"
else
    echo "Python 3 was not found. Install Python 3, then open this launcher again."
    echo "See the README in this folder."
    read -r -p "Press Enter to close..." ignored
    exit 1
fi

status=$?
if [ "$status" -ne 0 ]; then
    read -r -p "Press Enter to close..." ignored
fi
exit "$status"
