FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/catalog-service/generated/src
WORKDIR /app/catalog-service/generated

COPY catalog-service/generated/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY catalog-service/generated/src ./src
COPY scripts/seed.py /app/scripts/seed.py

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
