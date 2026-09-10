"""Scrapy settings for bounded, cached collection."""

BOT_NAME = "vandy_tv_news"
SPIDER_MODULES = ["vandy_tv_news.spiders"]
USER_AGENT = "vandy-tv-news/1.0 (+https://github.com/notnews/vandy_tv_news_abstracts)"
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2
HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = "data/httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [401, 403, 404, 429, 500, 502, 503, 504]
LOG_LEVEL = "INFO"
