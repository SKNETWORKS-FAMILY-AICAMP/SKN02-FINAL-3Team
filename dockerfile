FROM python:3.10-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip

# requirements.txt 파일 복사 및 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행 명령어
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]