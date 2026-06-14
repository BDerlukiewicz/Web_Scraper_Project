FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY web-scraper-engine /app/web-scraper-engine

WORKDIR /app/web-scraper-engine

CMD ["python", "api.py"]