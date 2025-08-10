FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# DB sẽ mount vào /app/data khi chạy trên server
VOLUME ["/app/data"]

CMD ["python", "main.py"]