from __future__ import annotations

import asyncio
import time

try:
    import aiohttp
except ImportError as exc:
    raise SystemExit(
        "Для запуска async_parser.py установите aiohttp: pip install aiohttp"
    ) from exc

from parser_common import (
    PARSER_WORKERS_COUNT,
    REQUEST_TIMEOUT,
    URLS,
    ParsedPage,
    build_task_title,
    extract_title,
    print_result,
    save_title_to_db,
    split_urls,
)


async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save(session: aiohttp.ClientSession, url: str) -> ParsedPage:
    try:
        html = await fetch_html(session, url)
        title = extract_title(html)
        task_id, action = await asyncio.to_thread(save_title_to_db, url, title)
        result = ParsedPage(
            url=url,
            title=build_task_title(title, url),
            task_id=task_id,
            action=action,
        )
        print_result(result)
        return result
    except Exception as exc:
        result = ParsedPage(
            url=url,
            title="",
            task_id=None,
            action="failed",
            error=str(exc),
        )
        print_result(result)
        return result


async def worker(session: aiohttp.ClientSession, urls: list[str]) -> list[ParsedPage]:
    results = []

    for url in urls:
        results.append(await parse_and_save(session, url))

    return results


async def run_parser() -> None:
    url_chunks = split_urls(URLS, PARSER_WORKERS_COUNT)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    start_time = time.perf_counter()

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [
            asyncio.create_task(worker(session, chunk))
            for chunk in url_chunks
        ]
        chunk_results = await asyncio.gather(*tasks)

    results = [result for chunk in chunk_results for result in chunk]
    elapsed_time = time.perf_counter() - start_time
    successful_count = sum(result.error is None for result in results)

    print("Подход: async/await")
    print(f"Количество асинхронных задач: {len(url_chunks)}")
    print(f"Успешно обработано страниц: {successful_count}/{len(URLS)}")
    print(f"Время выполнения: {elapsed_time:.6f} секунд")


def main() -> None:
    asyncio.run(run_parser())


if __name__ == "__main__":
    main()
