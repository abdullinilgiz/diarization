FROM python:3.10

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y ffmpeg

COPY app app

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]