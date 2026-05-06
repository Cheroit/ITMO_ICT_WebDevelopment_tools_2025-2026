from __future__ import annotations

import os
import threading
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


def worker(index: int, start: int, end: int, results: list[int]) -> None:
    results[index] = calculate_sum(start, end)


def main() -> None:
    ranges = split_range(NUMBER_LIMIT, WORKERS_COUNT)
    results = [0] * WORKERS_COUNT
    threads = []

    start_time = time.perf_counter()

    for index, (range_start, range_end) in enumerate(ranges):
        thread = threading.Thread(
            target=worker,
            args=(index, range_start, range_end, results),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    elapsed_time = time.perf_counter() - start_time
    expected_sum = calculate_sum(1, NUMBER_LIMIT)

    print("Подход: threading")
    print(f"Количество задач: {WORKERS_COUNT}")
    print(f"Сумма: {total_sum}")
    print(f"Проверка результата: {total_sum == expected_sum}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


if __name__ == "__main__":
    main()
