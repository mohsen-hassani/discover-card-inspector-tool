FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir flask gunicorn

COPY app/ ./app/
COPY main.py .

RUN mkdir -p /data/uploads

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "120", "main:app"]
