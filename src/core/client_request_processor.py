from typing import Any


def get_client_inputs(request: dict) -> tuple[Any, ...]:
    start_urls: list[str] = request.get('links', [])
    keywords: list[str] = request.get('keywords', [])
    categories: list[str] = request.get('categories', ["latest"])
    filter_fields: list[str] = request.get('filterFields', [])
    max_articles: int = request.get('maxArticles', 100)
    stop_date: str = request.get('stopDate', 'anytime')
    proxy_cfg: dict = request.get('proxyCfg')

    return start_urls, keywords, categories, filter_fields, max_articles, stop_date, proxy_cfg
