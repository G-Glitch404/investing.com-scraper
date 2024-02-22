BOT_NAME = "InvestingCrawler"
SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"

CLOSESPIDER_ITEMCOUNT = 100
DEPTH_LIMIT = 1000
ALLOWED_DATE_RANGE = 'anytime'
START_URLS = ['https://www.investing.com/news/most-popular-news/']

DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = True

# LOG_FILE = 'scrapy.log'
# LOG_FILE_APPEND = False
LOG_LEVEL = 'INFO'


ITEM_PIPELINES = {
    'src.pipelines.InvestingSpiderPipeline': 100
}
DOWNLOADER_MIDDLEWARES = {
    "src.middlewares.InvestingNewsFakeHeadersMiddleware": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
