FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./ /app
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
