import datetime as dt
from typing import Any, Optional

from apify import Actor

from src.settings import settings
from src.core.logger import Logger
from src.api.crawling_manager import crawling_manager
from src.util.utils import format_date

control_logger = Logger("Control")


def get_client_inputs(actor_input: dict) -> dict[str, Any]:
    start_urls: Optional[list[dict]] = actor_input.get('links', [])
    keywords: Optional[list[str]] = actor_input.get('keywords', [])
    categories: list[str] = actor_input.get('categories', ["latest"])
    filter_fields: Optional[list[dict]] = actor_input.get('filterFields', [])
    max_articles: int = actor_input.get('maxArticles', 100)
    stop_date: Optional[str] = actor_input.get('stopDate', 'anytime')
    proxy: Optional[dict] = actor_input.get('proxyConfiguration', {"useApifyProxy": False})

    return {
        "start_urls": [url.get('url') for url in start_urls],
        "keywords": keywords,
        "categories": categories,
        "filter_fields": filter_fields,
        "max_articles": max_articles,
        "stop_date": format_date(stop_date),
        "proxy_cfg": proxy
    }


async def main() -> None:
    """
     Apify Actor's main coroutine for executing the crawler
    """

    async with Actor:
        control_logger.info('Actor Initialized processing inputs...')

        await Actor.set_status_message('Processing input and configuring crawler settings...')
        actor_input: dict[str, Any] = get_client_inputs(await Actor.get_input() or {})
        await Actor.set_status_message('Configuring proxies if any were provided...')

        proxies: list[str] = []
        if proxy_cfg := await Actor.create_proxy_configuration(actor_input["proxy_cfg"]):
            requests_amount: int = len(actor_input["start_urls"]) or len(actor_input["categories"])
            proxies: list[str] = [(await proxy_cfg.new_url()) for _ in range(requests_amount)]

        control_logger.info(
            f"""\n
            Actor-Inputs - run date: {settings["TODAY_DATE"]}
            \n
            -----------------
            start_urls: {actor_input["start_urls"]}
            categories: {actor_input["categories"]}
            keyword: {actor_input["keywords"]}
            filter_fields: {actor_input["filter_fields"]}
            date_range: {actor_input["stop_date"]}
            max_articles: {actor_input["max_articles"]}
            proxies: {proxies}
            -----------------
            \n
            Crawling Initiated...
            """
        )

        if len(actor_input["start_urls"]) > 1:
            await Actor.set_status_message(
                f'Scraping ~{actor_input["max_articles"]} {"articles" if actor_input["max_articles"] > 1 else "article"} '
                f'from {len(actor_input["start_urls"])} {"links" if len(actor_input["start_urls"]) > 1 else "link"} '
                f'filtering with {len(actor_input["categories"])} {"categories" if len(actor_input["categories"]) > 1 else "category"}'
            )
        else:
            await Actor.set_status_message(
                f'Scraping ~{actor_input["max_articles"]} {"articles" if actor_input["max_articles"] > 1 else "article"} '
                f'from {len(actor_input["categories"])} {"categories" if len(actor_input["categories"]) > 1 else "category"}'
            )

        await crawling_manager(actor_input)

        control_logger.info(
            f'Actor Finished Scraping - found {settings["ARTICLES_FOUND"].value} articles (duplications included) and took '
            f'{round((dt.datetime.now(tz=dt.timezone.utc) - settings["TODAY_DATE"]).total_seconds() / 60, 2)}'
            f' minutes now exiting'
        )

        await Actor.set_status_message('Actor is done scraping now exiting...')
        await Actor.exit()


if __name__ == "__main__":
    Actor.run(main())
