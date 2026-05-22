import os
from typing import Any

import requests
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel

from core.celery_app import celery_app
from core.parser_tasks import parse_url_task


router = APIRouter(prefix="/parser", tags=["parser"])

PARSER_API_URL = os.getenv("PARSER_API_URL", "http://localhost:8001").rstrip("/")
PARSER_REQUEST_TIMEOUT = int(os.getenv("PARSER_REQUEST_TIMEOUT", "60"))


class ParseRequest(BaseModel):
    url: AnyHttpUrl


class ParseTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


def request_parser(url: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{PARSER_API_URL}/parse",
            json={"url": url},
            timeout=PARSER_REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service request failed: {exc}",
        ) from exc

    if response.status_code >= 400:
        try:
            detail: Any = response.json()
        except ValueError:
            detail = response.text

        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


@router.post("/parse")
def parse_via_parser_service(request: ParseRequest) -> dict[str, Any]:
    return request_parser(str(request.url))


@router.post("/parse/async", response_model=ParseTaskResponse)
def parse_via_queue(request: ParseRequest) -> ParseTaskResponse:
    task = parse_url_task.delay(str(request.url))
    return ParseTaskResponse(
        task_id=task.id,
        status="queued",
        message="Parsing task has been added to the Celery queue",
    )


@router.get("/parse/tasks/{task_id}")
def get_parse_task(task_id: str) -> dict[str, Any]:
    task = AsyncResult(task_id, app=celery_app)
    payload: dict[str, Any] = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        payload["result"] = task.result
    elif task.failed():
        payload["error"] = str(task.result)

    return payload
