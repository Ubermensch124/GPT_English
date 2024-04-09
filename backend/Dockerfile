FROM ubuntu:22.04

RUN apt update && apt install -y python3-pip ffmpeg

WORKDIR /app

COPY requirements-lock.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements-lock.txt

COPY . .

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]