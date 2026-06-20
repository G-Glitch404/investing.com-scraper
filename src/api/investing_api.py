import json
import time
import datetime as dt

from parsel import Selector
from seleniumbase import Driver
from selenium.common.exceptions import InvalidSessionIdException, NoSuchWindowException
from typing import Any, Optional, Union, Generator, Callable

from src.settings import settings
from src.items import Article
from src.core.logger import Logger
from src.util.utils import clean_text, to_datetime_aware, path
from src.util.selector import investing_com as se
from src.util.date_handler import convert_time_date

driver_exceptions: tuple = (
    json.JSONDecodeError, InvalidSessionIdException, NoSuchWindowException,
    KeyError, IndexError, TypeError, AttributeError
)


class InvestingAPI:
    logger = Logger("InvestingAPI")

    def __init__(self, worker_id: Optional[int] = None, proxy: dict = settings["PROXY"]) -> None:
        self._driver = None
        self.proxy: dict = proxy
        self.worker_id = worker_id

        self._crawling_category: str = ''
        self._format_date: Callable = lambda _date: convert_time_date(
            ''.join(_date.replace('<!-- --> <!-- -->', ' ').replace(', ', ',').split(' ', 1)[-1].split('<', 1)[0])
        )

        self.logger.info('InvestingAPI initialized successfully')

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.driver.quit()

    def __del__(self) -> None:
        self.driver.quit()

    @property
    def driver(self):
        """ Returns the seleniumbase uc driver """
        if self._driver is None or not self._driver.is_connected():
            self._driver = Driver(
                uc=True,
                headless2=True,
                proxy=self.proxy,
                browser='chrome',
                page_load_strategy="eager",
                dark_mode=True,
                do_not_track=True,
                user_data_dir=path(path('..', '.data_dirs'), f'InvestingCrawlerProfile{self.worker_id}'),
            )
            self.logger.debug("crawler started seleniumbase uc driver")

        return self._driver

    def pagination(self, topic: str, starting_page: int) -> Generator[str, None, None]:
        """
         generates page's urls for scraping articles

         :param topic: (str) name of topic or category to get the news from
         :param starting_page: (int) starting page number

         :yield: a page url as a str
        """
        categories: dict[str, str] = {
            "popular": 'news/most-popular-news',
            "stockmarket": 'news/stock-market-news',
            "stock_markets_analysis": 'analysis/stock-markets',
            "market_overview": 'analysis/market-overview',
            "trading": 'news/insider-trading-news',
            "commodities": 'news/commodities-news',
            "forex": 'news/forex-news',
            "ideas": 'news/investment-ideas',
            "swot": 'news/swot-analysis',
            "economics": 'news/economic-indicators',
            "sec_filings": 'news/sec-filings',
            "economy": 'news/economy',
            "world": 'news/world-news',
            "politics": 'news/politics',
            "companies": 'news/company-news',
            "general": 'news/general',
            "press_releases": 'news/press-releases',
            "earnings_reports": 'news/insider-trading-news',
            "cryptocurrencies": 'news/cryptocurrency-news',
            "bitcoin": 'crypto/bitcoin/news',
            "ethereum": 'crypto/ethereum/news',
            "xrp": 'crypto/xrp/news',
            "cardano": 'crypto/cardano/news',
            "sol": 'crypto/solana/news',
            "polkadot": 'crypto/polkadot-new/news',
            "shiba": 'crypto/shiba-inu/news',
            "dogecoin": 'crypto/dogecoin/news',
            "latest": 'news/latest-news',
        }

        category: str = categories.get(topic, categories["latest"])
        self._crawling_category: str = category

        while True:
            yield settings['INVESTING_ENDPOINT'] + f'/{category}/{starting_page}'
            starting_page += 1

    def crawl_page(self, link: str, stop_date: dt.datetime) -> Generator[Article, None, None]:
        self.driver.get(link)
        time.sleep(0.25)

        try: response: str = self.driver.page_source
        except AttributeError as e:
            self.logger.error(f"couldn't scrape articles from Investing-API - error: '{e}'")
            return

        selector = Selector(text=response, type='html')
        articles: list = selector.css(se['articles_section'])
        if len(articles) <= 0: articles: list = selector.css(se['analysis_section'])

        for article_html in articles:
            article_data: dict[str, Any] = {
                "title": clean_text(article_html.css(se['title']).extract()),
                "summary": clean_text(article_html.css(se['summary']).extract()),
                "publisher": clean_text(
                    [article_html.css(se['publisher_agency']).get() or article_html.css(se['article_writer']).get()]
                ),
                "url": article_html.css(se['url']).get()
            }

            if 'Investing.com Studios' in article_data['publisher'].strip():
                continue

            if article_obj := self.extract_article(article_data, stop_date):
                yield article_obj

    def crawl(
            self,
            topic_category: str = 'latest',
            stop_date: Optional[dt.datetime] = None,
            max_articles: int = 500,
            starting_page: int = 1,
    ) -> Generator[Article, None, None]:
        """
         extract articles from category page ready for requesting and scraping.

         :param topic_category: (str) name of topic or category to get the news from
         :param stop_date: (Optional[dt.datetime]) date to stop scraping articles when reached
         :param max_articles: (int) maximum number of articles to be scraped
         :param starting_page: (int) a page number to start scraping from

         :yield: Article object
        """
        self.logger.debug(f'started scraping category "{topic_category}" for "{max_articles}" articles')

        articles_counter: int = 0
        for url in self.pagination(topic_category, starting_page):
            self.logger.debug(f'crawling page number {url.split("/")[-1]}')
            for article in self.crawl_page(link=url, stop_date=stop_date):
                yield article
                articles_counter += 1
                if articles_counter >= max_articles:
                    self.logger.info(f'scrapped {articles_counter}/{max_articles} articles from "{topic_category}"')
                    return

    def extract_article(self, article: dict, stop_date: Optional[dt.datetime]) -> Union[Article, bool]:
        """ extract article data after collecting article url from main category page """
        self.driver.get(article['url'])
        time.sleep(0.25)
        try: article_page: str = self.driver.page_source
        except (AttributeError, TypeError) as e:
            self.logger.error(f"couldn't scrape article: {article['url']} from Investing-API - error: '{e}'")
            return False

        return self.parse(
            item_html=article_page,
            stop_date=stop_date,
            url=article['url'],
            title=article['title'],
            publisher=article['publisher'],
            summary=article['summary'],
        )

    def parse(
        self,
        item_html: str,
        stop_date: Optional[dt.datetime],
        url: str,
        title: str,
        publisher: str,
        summary: str,
    ) -> Union[Article, bool]:
        """ extract article data after collecting article url from main category page """
        article = Article()

        article['body']: Selector = Selector(text=item_html, type='html')

        dates: list[str] = article['body'].css(se['published_modified_dates']).getall()
        for date in dates:
            if 'Published' in date: article['published'] = self._format_date(date)
            if 'Updated' in date: article['modified'] = self._format_date(date)
            if article['published'] and article['modified']: break

        # date is already UTC
        if (
            not isinstance(stop_date, dt.datetime) or
            not isinstance(article["published"], dt.datetime) or
            article["published"] < to_datetime_aware(stop_date)
        ):
            return False

        article['publisher'] = publisher
        article['title'] = title
        article['url'] = url

        article['article_type'] = 'news'
        if self._crawling_category in ["stock_markets_analysis", "market_overview"]:
            article['article_type'] = 'analysis'

        article['category'] = self._crawling_category.lower().replace('_', ' ').split('/')[1]
        article['tags'] = ["Investing Article", article['category'].split('/')[1], article['article_type']]
        article['summary'] = summary.replace('-- ', '  ').replace(') -', '  ').split('  ', 1)[-1] or None

        article['images'] = [
            img for img in article['body'].css(se['images']).getall()
            if "/" in img and '.' in img and 'http' in img
        ] or None

        article['icon'] = article['images'][0] if article['images'] else (article['body'].css(se['icon']).get() or None)

        article['authors'] = [clean_text(author) for author in article['body'].css(se['authors']).extract()]
        if not article['authors']:
            article['authors'] = article['body'].css(se['authors_2']).extract_first('')
            if 'By ' in article['authors']:
                article['authors'] = article['authors'].replace('By ', '').lower()
            else: article['authors'] = None

        article['body'] = clean_text(
            ' '.join(article['body'].css(se['content']).extract())
        )

        return article


if __name__ == '__main__':
    _session = InvestingAPI()
    _start: float = time.perf_counter()

    _counter: int = 0
    _urls: set[str] = set()  # for detecting duplicates
    for __article in _session.crawl(
            topic_category='latest',
            stop_date=dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=5),
            max_articles=334
    ):
        __article.insert_to_db()
        _urls.add(__article['url'])
        for k, v in __article:
            print(f'{k}: {v}')
        print('-' * 100)
        _counter += 1

    _end: float = time.perf_counter()
    print(f'\nFound {_counter} articles in {round(_end - _start, 1)} secs')
    print(f'URLs: {len(_urls)}/{_counter}')
