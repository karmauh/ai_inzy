FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y fonts-dejavu fonts-dejavu-extra && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
