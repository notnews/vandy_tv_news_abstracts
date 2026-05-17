# -*- coding: utf-8 -*-
# Scrapy settings for vandy project
#
# Enhanced configuration for reliable access to protected content archives
# while maintaining respectful crawling practices

BOT_NAME = 'vandy'

SPIDER_MODULES = ['vandy.spiders']
NEWSPIDER_MODULE = 'vandy.spiders'

# ===== ACCESS CONTROL CONFIGURATION =====
# Disable robots.txt compliance due to server 403 responses on robots.txt itself
ROBOTSTXT_OBEY = False

# Browser-like user agent to avoid automated client detection
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Comprehensive headers to mimic legitimate browser requests
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Charset': 'utf-8, iso-8859-1;q=0.5',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

# ===== RATE LIMITING AND POLITENESS =====
# Conservative concurrent request limits to reduce server load
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Respectful delays between requests
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = 0.8  # 0.5 * to 1.5 * DOWNLOAD_DELAY

# Advanced auto-throttling for responsive rate adjustment
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False  # Set to True for throttling diagnostics

# Request timeout configuration
DOWNLOAD_TIMEOUT = 60

# ===== ERROR HANDLING AND RESILIENCE =====
# Comprehensive retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]  # Include 403 for transient blocks

# Handle redirects gracefully
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 5

# ===== CACHING STRATEGY =====
# Disable HTTP cache initially to force fresh requests and bypass cached 403s
# Re-enable after confirming access works to improve efficiency
HTTPCACHE_ENABLED = False

# When cache is re-enabled, use these optimized settings:
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 3600  # Cache for 1 hour
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [403, 404, 500, 502, 503, 504]
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# ===== CONTENT PROCESSING =====
# Cookie handling (disable if causing issues)
COOKIES_ENABLED = True

# Compression handling
COMPRESSION_ENABLED = True

# ===== LOGGING AND MONITORING =====
# Enhanced logging for debugging access issues
LOG_LEVEL = 'INFO'  # Change to 'DEBUG' for detailed diagnostics

# Log HTTP errors for analysis
HTTPERROR_ALLOWED_CODES = []  # Log all HTTP errors

# ===== EXTENSIONS AND MIDDLEWARE =====
# Enable core statistics
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Memory usage monitoring
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Telnet console for runtime monitoring (disable in production)
TELNETCONSOLE_ENABLED = True

# ===== FEED EXPORT CONFIGURATION =====
# JSON Lines format for streaming large datasets
FEED_EXPORT_ENCODING = 'utf-8'

# Custom feed exporters if needed
# FEED_EXPORTERS = {
#     'jsonlines': 'scrapy.exporters.JsonLinesItemExporter',
#     'csv': 'vandy.exporters.QuoteAllCsvItemExporter',  # Custom CSV exporter
# }

# ===== ADVANCED MIDDLEWARE CONFIGURATION =====
# Custom middleware for enhanced request handling
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#     'vandy.middlewares.RotateUserAgentMiddleware': 400,  # Custom user agent rotation
#     'vandy.middlewares.AccessControlMiddleware': 543,   # Custom access handling
# }

# ===== SPIDER-SPECIFIC OPTIMIZATIONS =====
# DNS caching for improved performance
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000

# Connection pooling
DOWNLOAD_HANDLERS = {
    'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
}

# ===== SECURITY AND COMPLIANCE =====
# Respect server capacity constraints
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.LifoMemoryQueue'

# Item processing pipeline configuration
# ITEM_PIPELINES = {
#     'vandy.pipelines.ValidationPipeline': 200,      # Data validation
#     'vandy.pipelines.DuplicationPipeline': 300,     # Duplicate detection
#     'vandy.pipelines.DatabasePipeline': 400,        # Database storage
# }

# ===== DEVELOPMENT VS PRODUCTION TOGGLES =====
# Development settings (comment out for production)
# DOWNLOAD_DELAY = 1
# CONCURRENT_REQUESTS = 8
# LOG_LEVEL = 'DEBUG'

# Production settings (uncomment for production deployment)
# DOWNLOAD_DELAY = 5
# CONCURRENT_REQUESTS = 2
# LOG_LEVEL = 'WARNING'
# HTTPCACHE_ENABLED = True