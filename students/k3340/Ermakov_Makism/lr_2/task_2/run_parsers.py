from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROGRAMS = [
    "threading_parser.py",
    "multiprocessing_parser.py",
    "async_parser.py",
]


def main() -> None:
    current_dir = Path(__file__).resolve().parent

    for program in PROGRAMS:
        print("=" * 60, flush=True)
        completed_process = subprocess.run(
            [sys.executable, str(current_dir / program)],
        )

        if completed_process.returncode != 0:
            print(f"Программа {program} завершилась с ошибкой.")
            break


if __name__ == "__main__":
    main()
