FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -e ".[test]"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
