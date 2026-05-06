from __future__ import annotations

import multiprocessing
import time

from parser_common import PARSER_WORKERS_COUNT, URLS, ParsedPage, parse_and_save_sync, split_urls


def parse_and_save(url: str) -> ParsedPage:
    return parse_and_save_sync(url)


def worker(urls: list[str]) -> list[ParsedPage]:
    return [parse_and_save(url) for url in urls]


def main() -> None:
    url_chunks = split_urls(URLS, PARSER_WORKERS_COUNT)

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=PARSER_WORKERS_COUNT) as pool:
        chunk_results = pool.map(worker, url_chunks)

    results = [result for chunk in chunk_results for result in chunk]
    elapsed_time = time.perf_counter() - start_time
    successful_count = sum(result.error is None for result in results)

    print("Подход: multiprocessing")
    print(f"Количество процессов: {PARSER_WORKERS_COUNT}")
    print(f"Успешно обработано страниц: {successful_count}/{len(URLS)}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
