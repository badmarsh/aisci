FROM python:3.11-slim
RUN apt-get update -qq && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn httpx
COPY main.py /app/main.py
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
