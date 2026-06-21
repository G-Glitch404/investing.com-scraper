import datetime as dt
from typing import Any, Optional

from apify import Actor

from src.settings import settings, crawler_categories
from src.core.logger import Logger
from crawling_manager import crawling_manager
from src.util.utils import format_date

control_logger = Logger("Control")


def get_client_inputs(actor_input: dict) -> dict[str, Any]:
    start_urls: Optional[list[dict]] = actor_input.get('links', [])
    proxy: Optional[dict] = actor_input.get('proxyConfiguration', {"useApifyProxy": False})
    keywords: Optional[list[str]] = actor_input.get('keywords', [])
    categories: list[str] = actor_input.get('categories', ["latest-news"])
    filter_fields: Optional[list[dict]] = actor_input.get('filterFields', [])
    max_articles: int = actor_input.get('maxArticles', 100)
    stop_date: Optional[str] = actor_input.get('stopDate')

    if proxy == {"useApifyProxy": False}:
        proxy = None

    if isinstance(categories, list) and len(categories) > 1:
        for k in crawler_categories["special_categories"]:
            if k not in categories: continue
            categories.pop(categories.index(k))
            categories += crawler_categories[k]

    return {
        "links": [url.get('url') for url in start_urls],
        "keywords": keywords,
        "categories": categories,
        "filter_fields": filter_fields,
        "max_articles": max_articles,
        "stop_date": format_date(stop_date) if stop_date else None,
        "proxy_cfg": proxy
    }


async def main() -> None:
    """ Apify Actor's main coroutine for executing the Actor """
    async with Actor:
        control_logger.info('Actor Initialized processing inputs...')

        await Actor.set_status_message('Processing input and configuring crawler settings...')
        actor_input: dict[str, Any] = get_client_inputs(await Actor.get_input() or {})
        await Actor.set_status_message('Configuring proxies if any were provided...')

        if actor_input["proxy_cfg"]:
            proxy_cfg = await Actor.create_proxy_configuration(actor_proxy_input=actor_input["proxy_cfg"])
            actor_input['proxy'] = await proxy_cfg.new_url()
        else: actor_input['proxy'] = None

        control_logger.info(
            f"""\n
            Actor-Inputs - run date: {settings["TODAY_DATE"]}
            \n
            -----------------
            start_urls: {actor_input["links"]}
            categories: {actor_input["categories"]}
            keyword: {actor_input["keywords"]}
            filter_fields: {actor_input["filter_fields"]}
            date_range: {actor_input["stop_date"]}
            max_articles: {actor_input["max_articles"]}
            proxies: {actor_input["proxy"]}
            -----------------\n
            Crawling Initiated...
            """
        )

        if len(actor_input["links"]) > 1:
            await Actor.set_status_message(
                f'Scraping ~{actor_input["max_articles"]} {"articles" if actor_input["max_articles"] > 1 else "article"} '
                f'from {len(actor_input["links"])} {"links" if len(actor_input["links"]) > 1 else "link"} '
                f'filtering with {len(actor_input["categories"])} {"categories" if len(actor_input["categories"]) > 1 else "category"}'
            )
        else:
            await Actor.set_status_message(
                f'Scraping ~{actor_input["max_articles"]} {"articles" if actor_input["max_articles"] > 1 else "article"} '
                f'from {len(actor_input["categories"])} {"categories" if len(actor_input["categories"]) > 1 else "category"}'
            )

        await crawling_manager(Actor, actor_input)

        control_logger.info(
            f'Actor Finished Scraping - found {settings["ARTICLES_FOUND"].value} articles (duplications included) and took '
            f'{round((dt.datetime.now(tz=dt.timezone.utc) - settings["TODAY_DATE"]).total_seconds() / 60, 2)}'
            f' minutes now exiting'
        )

        await Actor.set_status_message('Actor is done scraping now exiting...')
        await Actor.exit()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
