import logging
import datetime as dt

from multiprocessing import Value
from .util.utils import path


settings = {
    "INVESTING_ENDPOINT": "https://www.investing.com",

    "VERBOSE": False,
    "LOGGING_LEVEL": logging.DEBUG,

    "DATABASE": path(
        path('..', '.db'), path('.db', 'articles.db')
    ),

    "PROXY": None,
    "MAX_ARTICLES": 100,
    "STOP_DATE": dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=2),
    "WORKERS": 2,
    "ARTICLES_FOUND": Value('i', 0),

    "CATEGORIES_LEN": 27,  # change it when categories are changed downside
    "INVESTING_CATEGORIES": ("popular", "stockmarket", "commodities", "forex", "economics", "economy", "world", "politics", "stock_markets_analysis", "market_overview", "trading", "ideas", "swot", "sec_filings", "press_releases", "earnings_reports", "companies", "general", "cryptocurrencies", "bitcoin", "ethereum", "xrp", "cardano", "sol", "polkadot", "shiba", "dogecoin"),
}
