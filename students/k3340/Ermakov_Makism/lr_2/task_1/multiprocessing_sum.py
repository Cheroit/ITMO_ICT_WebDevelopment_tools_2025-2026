from __future__ import annotations

import multiprocessing
import os
import time


NUMBER_LIMIT = 10_000_000_000_000
WORKERS_COUNT = min(8, os.cpu_count() or 4)


def calculate_sum(start: int, end: int) -> int:
    """Return the sum of all integers in the inclusive range [start, end]."""
    return (start + end) * (end - start + 1) // 2


def split_range(limit: int, parts: int) -> list[tuple[int, int]]:
    chunk_size = limit // parts
    ranges = []
    current_start = 1

    for part_index in range(parts):
        current_end = limit if part_index == parts - 1 else current_start + chunk_size - 1
        ranges.append((current_start, current_end))
        current_start = current_end + 1

    return ranges


def main() -> None:
    ranges = split_range(NUMBER_LIMIT, WORKERS_COUNT)

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=WORKERS_COUNT) as pool:
        partial_sums = pool.starmap(calculate_sum, ranges)

    total_sum = sum(partial_sums)
    elapsed_time = time.perf_counter() - start_time
    expected_sum = calculate_sum(1, NUMBER_LIMIT)

    print("Подход: multiprocessing")
    print(f"Количество процессов: {WORKERS_COUNT}")
    print(f"Сумма: {total_sum}")
    print(f"Проверка результата: {total_sum == expected_sum}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
