FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu fonts-dejavu-extra && rm -rf /var/lib/apt/lists/*

# Torch w wariancie CPU (bez CUDA) – znacznie mniejszy obraz
RUN pip install --no-cache-dir torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
