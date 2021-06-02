# -*- coding: utf-8 -*-

# Scrapy settings for newscrawlers project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os

# BOT_NAME = 'newscrawlers'
BOT_NAME = 'fandango_news_crawler'

SPIDER_MODULES = ['newscrawlers.spiders']
NEWSPIDER_MODULE = 'newscrawlers.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'newscrawlers (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/64.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Address of the Splash instance running
SPLASH_URL = 'http://localhost:8050/'

# Scrapy Splash specific
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# Only if you use Scrapy HTTP cache
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = True
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    # 'newscrawlers.middlewares.NewsCrawlerSpiderMiddleware': 1,
    # 'scrapy_crawl_once.CrawlOnceMiddleware': 50,
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    # 'scrapy.spidermiddlewares.referer.RefererMiddleware': None,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 555,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'newscrawlers.middlewares.NewsCrawlerDownloaderMiddleware': 1,

    # 'scrapy_crawl_once.CrawlOnceMiddleware': 50,
    # 'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    # "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": 711,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'newscrawlers.pipelines.StdOutJsonPipeline': 200,
    'newscrawlers.pipelines.ElasticSearchPipeline': 300,
    'scrapy_elastic.pipelines.CrawlOnce': 350,
    'newscrawlers.pipelines.KafkaJsonPipeline': 400,
}

# # Set crawling order to Breadth-First (instead of Depth-First)
# DEPTH_PRIORITY = 1
# SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

SCHEDULER = "scrapy_elastic.scheduler.ElasticScheduler"
ELASTIC_SERVER = os.getenv('ELASTIC_SERVER', "83.212.123.15")
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200)) 
# ELASTIC_USERNAME = ""
# ELASTIC_PASSWORD = ""

ELASTIC_INDEX = os.getenv('ELASTIC_INDEX', "scrapy-scheduler")
ELASTIC_TYPE = "request"

ELASTIC_QUEUE_CLASS = "scrapy_elastic.queue.FifoQueue"
# ELASTIC_QUEUE_CLASS = "scrapy_elastic.queue.LifoQueue"
# ELASTIC_QUEUE_CLASS = "scrapy_elastic.queue.PriorityQueue"

ELASTIC_DUPEFILTER_CLASS = "scrapy_elastic.dupefilter.ElasticDupeFilter"

SCHEDULER_PERSIST = True
SCHEDULER_FLUSH_ON_START = False
SCHEDULER_IDLE_BEFORE_CLOSE = 0
SCHEDULER_PER_SPIDER = True


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Export as CSV Feed
# FEED_FORMAT = "json"
# Use the spiders name for output file
# FEED_URI = 'tmp/%(name)s.json'

# # Settings for scrapy_crawl_once
# CRAWL_ONCE_PATH = 'crawl_once/'
# CRAWL_ONCE_ENABLED = True
# CRAWL_ONCE_DEFAULT = True

# set stdout log to error level in order to avoid messages (Nifi Flowfiles)
# LOG_LEVEL = 'ERROR'
# LOG_LEVEL = 'INFO'
