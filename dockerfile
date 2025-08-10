FROM python:3.12-slim

WORKDIR /app

# Copy file requirements từ thư mục TOOL
COPY TOOL/requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code từ thư mục TOOL
COPY TOOL/ . 

# DB sẽ mount vào /app/data khi chạy trên server
VOLUME ["/mnt/scrappers/database"]

CMD ["python", "main.py"]
