import os

import requests

from core.celery_app import celery_app


PARSER_API_URL = os.getenv("PARSER_API_URL", "http://localhost:8001").rstrip("/")
PARSER_REQUEST_TIMEOUT = int(os.getenv("PARSER_REQUEST_TIMEOUT", "60"))


@celery_app.task(name="parse_url")
def parse_url_task(url: str) -> dict:
    response = requests.post(
        f"{PARSER_API_URL}/parse",
        json={"url": url},
        timeout=PARSER_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
