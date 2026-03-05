import datetime as dt
from typing import Any, Optional

from src.util.utils import format_date


def get_client_inputs(actor_input: dict) -> tuple[Any, ...]:
    start_urls: Optional[list[dict]] = actor_input.get('links', [])
    keywords: Optional[list[str]] = actor_input.get('keywords', [])
    categories: list[str] = actor_input.get('categories', ["latest"])
    filter_fields: Optional[list[dict]] = actor_input.get('filterFields', [])
    max_articles: int = actor_input.get('maxArticles', 100)
    stop_date: Optional[str] = actor_input.get('stopDate', 'anytime')
    proxies: Optional[dict] = actor_input.get('proxyConfiguration', {"useApifyProxy": False})

    start_urls: list[str] = [url.get('url') for url in start_urls]
    stop_date: dt.datetime = format_date(stop_date)

    return start_urls, keywords, categories, filter_fields, max_articles, stop_date, proxies
