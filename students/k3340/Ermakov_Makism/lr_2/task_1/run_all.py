from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROGRAMS = [
    "threading_sum.py",
    "multiprocessing_sum.py",
    "async_sum.py",
]


def main() -> None:
    current_dir = Path(__file__).resolve().parent

    for program in PROGRAMS:
        print("=" * 60, flush=True)
        subprocess.run(
            [sys.executable, str(current_dir / program)],
            check=True,
        )


if __name__ == "__main__":
    main()
