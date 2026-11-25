FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/provider-service/generated/src

WORKDIR /app/provider-service/generated

COPY provider-service/generated/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY provider-service/generated/src ./src

EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=20 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/ready', timeout=2).close()"]

CMD ["python", "-m", "uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
