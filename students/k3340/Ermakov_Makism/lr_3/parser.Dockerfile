FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/lr_2/task_2:/app/lr_1/lab_1:/app/lr_3

WORKDIR /app

COPY lr_3/requirements-parser.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY lr_1/lab_1 /app/lr_1/lab_1
COPY lr_2/task_2 /app/lr_2/task_2
COPY lr_3/parser_service /app/lr_3/parser_service

CMD ["uvicorn", "parser_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
