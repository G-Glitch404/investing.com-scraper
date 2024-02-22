from __future__ import annotations

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from apify import Actor

# Import your Scrapy spider here
from src.spiders.InvestingScraper import InvestingscraperSpider as Spider

import datetime
import math

# Default input values for local execution using `apify run`
LOCAL_DEFAULT_START_URLS = [
    {"url": "https://www.investing.com/news/latest-news/"},
    {"url": "https://www.investing.com/news/most-popular-news/"},
    {"url": "https://www.investing.com/news/headlines/"},
    {"url": "https://www.investing.com/news/cryptocurrency-news/"},
    {"url": "https://www.investing.com/news/stock-market-news/"},
    {"url": "https://www.investing.com/news/commodities-news/"},
    {"url": "https://www.investing.com/news/forex-news/"},
    {"url": "https://www.investing.com/news/economy/"},
    {"url": "https://www.investing.com/news/economic-indicators/"},
    {"url": "https://www.investing.com/news/politics/"},
    {"url": "https://www.investing.com/news/world-news/"}
]


def date_range_handle(requested_date_range: str) -> tuple[datetime.date, datetime.date] | datetime.date | str:
    if requested_date_range == 'anytime':
        return requested_date_range

    elif '-' not in requested_date_range and '/' in requested_date_range:
        return datetime.date(*list(map(int, requested_date_range.split('/'))))

    elif '-' in requested_date_range and '/' in requested_date_range:
        date = requested_date_range.split('-')
        start_date = datetime.date(*list(map(int, date[0].split('/'))))
        end_date = datetime.date(*list(map(int, date[1].split('/'))))

        return start_date, end_date

    elif any([word in requested_date_range for word in ['day', 'week', 'year', 'month']]):
        if 'day' in requested_date_range:
            days_amount = int(requested_date_range.replace('day', ''))
        elif 'week' in requested_date_range:
            days_amount = math.floor(float(requested_date_range.replace('week', '')) * 7)
        elif 'month' in requested_date_range:
            days_amount = math.floor(float(requested_date_range.replace('month', '')) * 30)
        elif 'year' in requested_date_range:
            days_amount = math.floor(float(requested_date_range.replace('year', '')) * 365.25)
        else:
            raise Exception(f"{requested_date_range} date requested is malformed can't be processed")

        today = datetime.datetime.today().date()
        return today, today - datetime.timedelta(days=days_amount)

    else:
        raise Exception(f"{requested_date_range} date requested is malformed can't be processed")


def __get_scrapy_settings(start_urls, max_articles: int, date_range: str, proxy_cfg: dict | None = None) -> Settings:
    settings = get_project_settings()
    settings['ITEM_PIPELINES']['src.pipelines.ActorPushPipeline'] = 1000

    # Disable the default RobotsTxtMiddleware, Apify's custom scheduler already handles robots.txt
    settings['DOWNLOADER_MIDDLEWARES']['scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware'] = None

    # Disable the default HttpProxyMiddleware and add ApifyHttpProxyMiddleware
    settings['DOWNLOADER_MIDDLEWARES']['scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware'] = None
    settings['DOWNLOADER_MIDDLEWARES']['apify.scrapy.middlewares.ApifyHttpProxyMiddleware'] = 950

    # Store the proxy configuration
    settings['APIFY_PROXY_SETTINGS'] = proxy_cfg
    settings['CLOSESPIDER_ITEMCOUNT'] = max_articles
    settings['ALLOWED_DATE_RANGE'] = date_range
    settings['START_URLS'] = start_urls

    return settings


async def main() -> None:
    """
    Apify Actor main coroutine for executing the Scrapy spider.
    """

    async with Actor:
        Actor.log.info('Actor is being executed...')

        # Process Actor input
        actor_input = await Actor.get_input() or {}

        start_urls = [url.get('url') for url in actor_input.get('startUrls', LOCAL_DEFAULT_START_URLS)]
        date_range = actor_input.get('dateRange', None)
        max_articles = actor_input.get('maxArticles', 100)
        proxy_configuration = actor_input.get('proxyConfiguration')
        Actor.log.info(f'\nstart urls: {start_urls}\nmax articles: {max_articles}\ndate range: {date_range}\n')

        # Get Scrapy project settings with custom configurations
        if date_range:
            date_range = date_range_handle(date_range.lower().replace(" ", "").replace('s', ''))
        settings = __get_scrapy_settings(start_urls, int(max_articles), date_range, proxy_configuration)

        # Execute the spider using Scrapy CrawlerProcess
        Actor.log.info('Crawling Started...')

        process = CrawlerProcess(settings)
        process.crawl(Spider)
        process.start()
