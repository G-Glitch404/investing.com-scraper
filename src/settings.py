import logging
import datetime as dt

from typing import Any
from multiprocessing import Value

from src.util.utils import path


settings: dict[str, Any] = {
    "INVESTING_ENDPOINT": "https://www.investing.com",

    "VERBOSE": False,
    "LOGGING_LEVEL": logging.DEBUG,

    "DATABASE": path(
        path('..', '.db'), path('.db', 'articles.db')
    ),

    "TODAY_DATE": dt.datetime.now(tz=dt.timezone.utc),

    "PROXY": None,
    "MAX_ARTICLES": 100,
    "STOP_DATE": dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=2),
    "WORKERS": 2,
    "ARTICLES_FOUND": Value('i', 0),
}

crawler_categories: dict[str, Any] = {
    "categories_len": 27,  # change it when categories are changed downside
    "all_categories": ("popular", "stockmarket", "commodities", "forex", "economics", "economy", "world", "politics", "stock_markets_analysis", "market_overview", "trading", "ideas", "swot", "sec_filings", "press_releases", "earnings_reports", "companies", "general", "cryptocurrencies", "bitcoin", "ethereum", "xrp", "cardano", "sol", "polkadot", "shiba", "dogecoin"),
    "special_categories": ("stockmarket", "economy", "reports", "cryptocurrencies"),

    # special categories
    "stockmarket": ("stockmarket", "stock_markets_analysis", "market_overview"),
    "economy": ("economy", "commodities", "economics"),
    "reports": ("earnings_reports",  "ideas", "swot", "sec_filings", "press_releases"),
    "cryptocurrencies": ("cryptocurrencies", "bitcoin", "ethereum", "xrp", "cardano", "sol", "polkadot", "shiba", "dogecoin"),
}
