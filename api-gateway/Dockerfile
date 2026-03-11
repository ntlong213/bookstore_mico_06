FROM python:3.11-slim
WORKDIR /app

# Install MySQL client dependencies and netcat
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY wait-for-mysql.sh /wait-for-mysql.sh
RUN sed -i 's/\r//' /wait-for-mysql.sh && chmod +x /wait-for-mysql.sh
CMD ["/wait-for-mysql.sh", "mysql:3306", "python", "manage.py", "runserver", "0.0.0.0:8000"]