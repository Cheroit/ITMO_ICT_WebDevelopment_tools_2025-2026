from __future__ import annotations

import asyncio
import os
import time


NUMBER_LIMIT = 10_000_000_000_000
TASKS_COUNT = min(8, os.cpu_count() or 4)


async def calculate_sum(start: int, end: int) -> int:
    """Return the sum of all integers in the inclusive range [start, end]."""
    await asyncio.sleep(0)
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


async def run_calculation() -> None:
    ranges = split_range(NUMBER_LIMIT, TASKS_COUNT)

    start_time = time.perf_counter()

    tasks = [
        asyncio.create_task(calculate_sum(range_start, range_end))
        for range_start, range_end in ranges
    ]
    partial_sums = await asyncio.gather(*tasks)

    total_sum = sum(partial_sums)
    elapsed_time = time.perf_counter() - start_time
    expected_sum = (1 + NUMBER_LIMIT) * NUMBER_LIMIT // 2

    print("Подход: async/await")
    print(f"Количество асинхронных задач: {TASKS_COUNT}")
    print(f"Сумма: {total_sum}")
    print(f"Проверка результата: {total_sum == expected_sum}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


def main() -> None:
    asyncio.run(run_calculation())


if __name__ == "__main__":
    main()
