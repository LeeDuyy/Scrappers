FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install

ENV PYTHONPATH=/app

VOLUME ["/mnt/scrappers/database"]

CMD ["python", "main.py"]