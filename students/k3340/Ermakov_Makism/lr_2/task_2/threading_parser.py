from __future__ import annotations

import threading
import time

from parser_common import PARSER_WORKERS_COUNT, URLS, ParsedPage, parse_and_save_sync, split_urls


def parse_and_save(url: str) -> ParsedPage:
    return parse_and_save_sync(url)


def worker(urls: list[str], results: list[ParsedPage]) -> None:
    for url in urls:
        results.append(parse_and_save(url))


def main() -> None:
    url_chunks = split_urls(URLS, PARSER_WORKERS_COUNT)
    results: list[ParsedPage] = []
    threads = []

    start_time = time.perf_counter()

    for chunk in url_chunks:
        thread = threading.Thread(target=worker, args=(chunk, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed_time = time.perf_counter() - start_time
    successful_count = sum(result.error is None for result in results)

    print("Подход: threading")
    print(f"Количество потоков: {len(threads)}")
    print(f"Успешно обработано страниц: {successful_count}/{len(URLS)}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


if __name__ == "__main__":
    main()
