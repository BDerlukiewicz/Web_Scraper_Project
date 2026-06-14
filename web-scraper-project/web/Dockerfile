FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY web /app/web

WORKDIR /app

CMD ["python", "web/app.py"]