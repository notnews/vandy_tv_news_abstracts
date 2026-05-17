FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install scrapy
CMD ["scrapy", "crawl", "vandy_news", "-o", "broadcasts.json"]
