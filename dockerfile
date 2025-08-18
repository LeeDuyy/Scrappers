FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

# Copy requirements và cài Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-u", "main.py"]
