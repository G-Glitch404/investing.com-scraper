import math
import asyncio
import datetime as dt

from typing import Any

from src.settings import settings, crawler_categories
from src.api.investing_api import InvestingAPI
from src.core.database import Database
from src.core.logger import Logger
from src.util.utils import max_articles_per_category
from src.__init__ import rebuild_database, clean_processes

logger = Logger("CrawlingManager")


async def scrape_links(crawler, links: list[str], stop_date: dt.datetime, max_articles: int) -> None:
    def _run() -> None:
        articles_counter = 0
        for link in links:
            for article in crawler.crawl_page(link=link, stop_date=stop_date):
                if article.insert_to_db():
                    articles_counter += 1
                if articles_counter >= max_articles:
                    return

    await asyncio.to_thread(_run)


async def scrape_categories(crawler, categories: list[str], stop_date: dt.datetime, max_articles: int) -> None:
    def _run() -> None:
        articles_counter = 0
        for category in categories:
            for article in crawler.crawl(
                topic_category=category,
                max_articles=max_articles,
                stop_date=stop_date,
            ):
                if article.insert_to_db():
                    articles_counter += 1
                if articles_counter >= max_articles:
                    return

    await asyncio.to_thread(_run)


def article_filter(article: dict[str, Any], actor_input: dict[str, Any]) -> tuple[bool, str]:
    for field in actor_input["filter_fields"]:
        val = article.get(field)
        if not val:
            return True, f"missing field {field}"
        if isinstance(val, str) and val.strip() == "":
            return True, f"missing field {field}"
        if isinstance(val, (list, dict)) and len(val) == 0:
            return True, f"missing field {field}"

    if "all" not in actor_input["categories"]:
        art_cat = article.get("category")
        if not art_cat or art_cat not in crawler_categories["all_categories"]:
            return True, "article category unavailable"
        if art_cat not in actor_input["categories"]:
            return True, "category mismatch"

    if actor_input["keywords"]:
        art_text = article.get("body") or ""
        if not isinstance(art_text, str) or not art_text.strip():
            art_text = (article.get("title") or "") + (article.get("summary") or "")

        if not any(kw in art_text for kw in actor_input["keywords"]):
            return True, "no keywords matched"

    return False, ""


async def push_data(actor, actor_input: dict[str, Any], done: asyncio.Event) -> None:
    counter, retries = 0, 0
    while not done.is_set() or Database().fetch_all("articles"):
        await asyncio.sleep(2)

        rows = Database().fetch_all("articles")
        if not rows:
            retries += 1
            if done.is_set() and retries >= 3:
                break
            continue

        retries = 0

        for db_article in rows:
            if counter >= actor_input["max_articles"]:
                done.set()
                break

            authors = db_article[5].split(" , ") if db_article[5] else []
            tags = db_article[10].split(" , ") if db_article[10] else []
            images = db_article[13].split(" , ") if db_article[13] else []

            article = {
                "icon": db_article[1],
                "title": db_article[2],
                "summary": db_article[3],
                "publisher": db_article[4],
                "authors": authors,
                "category": db_article[6],
                "article_type": db_article[7],
                "published": db_article[8],
                "modified": db_article[9],
                "tags": tags,
                "body": db_article[11],
                "url": db_article[12],
                "images": images,
            }

            filter_status = article_filter(article, actor_input)
            if not filter_status[0]:
                await actor.push_data(article)
                counter += 1
            else: logger.warning(f"Dropped an article reason:  {filter_status[1]}  -  url:  {article['url']}")

            Database().delete_record(db_article[0])

    done.set()


async def crawling_manager(actor, actor_input: dict[str, Any]) -> None:
    rebuild_database()
    clean_processes()

    done = asyncio.Event()

    total_items = len(actor_input["links"]) if actor_input["links"] else len(actor_input["categories"])
    amount_per_category = max_articles_per_category(actor_input["max_articles"], total_items)
    cats_or_urls_per_worker = math.ceil(total_items / settings["WORKERS"])

    crawler = InvestingAPI(worker_id=1, proxy=(actor_input["proxy"] or None))

    tasks = [push_data(actor, actor_input, done)]

    if isinstance(actor_input["links"], list) and len(actor_input["links"]) >= 1:
        tasks.append(
            scrape_links(
                crawler=crawler,
                links=actor_input["links"][:cats_or_urls_per_worker],
                stop_date=actor_input["stop_date"],
                max_articles=amount_per_category,
            )
        )
    elif isinstance(actor_input["categories"], list) and len(actor_input["categories"]) >= 1:
        tasks.append(
            scrape_categories(
                crawler=crawler,
                categories=actor_input["categories"][:cats_or_urls_per_worker],
                stop_date=actor_input["stop_date"],
                max_articles=amount_per_category,
            )
        )

    await asyncio.gather(*tasks)
