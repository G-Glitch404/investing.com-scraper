from apify import Actor


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
