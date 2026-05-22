FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY lr_3/requirements-api.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY lr_1/lab_1 /app/lr_1/lab_1

WORKDIR /app/lr_1/lab_1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
