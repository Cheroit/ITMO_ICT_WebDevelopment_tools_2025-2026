from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import AnyHttpUrl, BaseModel

from parser_common import URLS, parse_and_save_sync


app = FastAPI(title="Time Manager Parser API")


class ParseRequest(BaseModel):
    url: AnyHttpUrl


def serialize_result(result) -> dict:
    return asdict(result)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Parser API is ready"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/urls")
def urls() -> dict[str, list[str]]:
    return {"urls": URLS}


@app.post("/parse")
def parse(request: ParseRequest) -> dict:
    result = parse_and_save_sync(str(request.url))

    if result.error:
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "message": "Parsing completed",
        "result": serialize_result(result),
    }


@app.post("/parse/default")
def parse_default_urls() -> dict:
    results = [parse_and_save_sync(url) for url in URLS]
    failed = [result for result in results if result.error]

    return {
        "message": "Default URL parsing completed",
        "total": len(results),
        "successful": len(results) - len(failed),
        "failed": len(failed),
        "results": [serialize_result(result) for result in results],
    }
