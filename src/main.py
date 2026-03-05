from apify import Actor
from typing import Any, Optional

from src.settings import settings


async def main() -> None:
    """
    Apify Actor main coroutine for executing the Scrapy spider.
    """

    async with Actor:
        Actor.log.info('Actor is being executed...')

        # Process Actor input
        actor_input = await Actor.get_input() or {}

        start_urls = [url.get('url') for url in actor_input.get('startUrls', [])]
        date_range = actor_input.get('dateRange', None)
        max_articles = actor_input.get('maxArticles', 100)
        proxy_configuration: Optional[dict] = actor_input.get('proxyConfiguration', {"useApifyProxy": False})
        await Actor.set_status_message('Configuring proxies if any were provided...')
        proxy_configuration: Any = await Actor.create_proxy_configuration(actor_proxy_input=proxy_configuration)
        if proxy_configuration:
            proxies: list = [proxy_configuration.new_url() for _ in range(len(start_urls))]
            if isinstance(proxies, list): settings['PROXIES'] = proxies

        Actor.log.info(f'\nstart urls: {start_urls}\nmax articles: {max_articles}\ndate range: {date_range}\n')

        if date_range:
            date_range = date_range_handle(date_range.lower().replace(" ", "").replace('s', ''))
        settings = __get_scrapy_settings(start_urls, int(max_articles), date_range, proxy_configuration)

        Actor.log.info('Crawling Started...')

