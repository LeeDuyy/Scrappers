FROM python:3.12-slim

WORKDIR /app

# Cài các dependencies cần cho Chromium
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libnspr4 \
    libnss3 \
    libnssutil3 \
    libdbus-1-3 \
    libgio-2.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libexpat1 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libasound2 \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài requirements Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài Chromium và dependencies
RUN playwright install --with-deps chromium

# Copy source code
COPY . .

ENV PYTHONPATH=/app

VOLUME ["/mnt/scrappers/database"]

CMD ["python", "main.py"]
