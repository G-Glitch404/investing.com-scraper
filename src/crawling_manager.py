import asyncio
import datetime as dt

from typing import Any, Optional, Coroutine, Generator

from items import Article
from src.settings import settings, crawler_categories
from src.crawler.investing_crawler import InvestingCrawler
from src.core.database import Database
from src.core.logger import Logger
from src.__init__ import rebuild_database, clean_processes

logger = Logger("CrawlingManager")


async def charge_user(actor, event_name: str) -> None:
    """ charge the user for an event """
    charge_event = await actor.charge(event_name=event_name)
    if charge_event.event_charge_limit_reached:
        logger.warning(f"charge event '{event_name}' limit reached, exiting...")
        await actor.exit()


def article_filter(article: dict[str, Any], actor_input: dict[str, Any]) -> tuple[bool, str]:
    """ checks if an article is valid to be returned or not """
    for field in actor_input["filter_fields"]:
        val: Any = article.get(field)
        if not val:
            return True, f"missing field {field}"
        if isinstance(val, str) and val.strip() == "":
            return True, f"missing field {field}"
        if isinstance(val, (list, dict)) and len(val) == 0:
            return True, f"missing field {field}"

    if "all" not in actor_input["categories"]:
        art_cat: Optional[str] = article.get("category")
        if not art_cat or art_cat not in crawler_categories["all_categories"]:
            return True, "article category unavailable"
        if art_cat not in actor_input["categories"]:
            return True, "category mismatch"

    if actor_input["keywords"]:
        art_text: str = article.get("body") or ""
        if not isinstance(art_text, str) or not art_text.strip():
            art_text: str = (article.get("title") or "") + (article.get("summary") or "")

        if not any(kw in art_text for kw in actor_input["keywords"]):
            return True, "no keywords matched"

    return False, ""


async def push_data(actor, actor_input: dict[str, Any], done: asyncio.Event) -> None:
    """ push the data to the apify platform storage """
    logger.debug(f'started the database consumer loop max_articles: {actor_input["max_articles"]}')
    retries: int = 0

    while not done.is_set() and settings["ARTICLES_FOUND"].value < actor_input["max_articles"]:
        await asyncio.sleep(10)

        rows: list[tuple[Any, ...]] = [row for row in Database().fetch_all("articles") if not row[1]]
        if not rows:
            retries += 1
            if done.is_set(): break
            if retries > 3:
                done.set()
                break
            continue

        retries = 0

        logger.debug(f"found {len(rows)} new articles in the database, consuming..")

        for db_article in rows:
            if settings["ARTICLES_FOUND"].value >= actor_input["max_articles"]:
                logger.debug(f"user got enough articles '{settings["ARTICLES_FOUND"].value}', forcing an immediate stop right now...")
                done.set()
                break

            Database().execute(f"UPDATE articles SET pushed=1 WHERE id = {db_article[0]};")

            authors: list[str] = db_article[6].split(" , ") if db_article[6] else []
            tags: list[str] = db_article[11].split(" , ") if db_article[11] else []
            images: list[str] = db_article[14].split(" , ") if db_article[14] else []

            article = {
                "icon": db_article[2],
                "title": db_article[3],
                "summary": db_article[4],
                "publisher": db_article[5],
                "authors": authors,
                "category": db_article[7],
                "article_type": db_article[8],
                "published": db_article[9],
                "modified": db_article[10],
                "tags": tags,
                "body": db_article[12],
                "url": db_article[13],
                "images": images,
            }

            filter_status = article_filter(article, actor_input)
            if not filter_status[0]:
                await actor.push_data(article)
                await charge_user(actor, 'pushed-result')
                logger.info("charged user for a valid article result")
                settings["ARTICLES_FOUND"].value += 1
            else: logger.warning(f"Dropped an article reason:  {filter_status[1]}  -  url:  {article['url']}")

    logger.info(f"push loop finished and exiting, found articles {settings["ARTICLES_FOUND"].value} article")
    done.set()


async def crawl_worker(
        crawler: InvestingCrawler,
        done: asyncio.Event,
        work_units: list[dict[str, Any]],
        max_articles_per_worker: int,
        stop_date: Optional[dt.datetime] = None,
) -> None:
    """ worker function for each worker """
    def _run() -> None:
        articles_counter: int = 0

        for item in work_units:
            if (articles_counter >= max_articles_per_worker) or done.is_set(): return

            item_type: str = item.get("type")
            remaining: int = max_articles_per_worker - articles_counter

            if item_type == "link":
                generator: Generator[Article, None, None] = crawler.crawl_page(
                    link=item["value"],
                    stop_date=stop_date,
                )

            elif item_type == "category":
                shard_step = int(item.get("shard_step", 1))
                starting_page = int(item.get("starting_page", 1))

                if shard_step > 1:
                    generator: Generator[Article, None, None] = _crawl_category_shard(
                        crawler=crawler,
                        done=done,
                        topic_category=item["value"],
                        stop_date=stop_date,
                        starting_page=starting_page,
                        shard_step=shard_step,
                    )
                else:
                    generator: Generator[Article, None, None] = crawler.crawl(
                        topic_category=item["value"],
                        max_articles=remaining,
                        stop_date=stop_date,
                    )

            else:
                logger.error("work provided for one of the workers contains invalid data 'type' is not in ('link', 'category'), worker is stopping now..")
                return

            for article in generator:
                if article.insert_to_db():
                    articles_counter += 1

                if articles_counter >= max_articles_per_worker:
                    logger.info(f"worker reached max articles limit '{max_articles_per_worker}', stopping now..")
                    return

    logger.info(f"worker crawl initiated for {len(work_units)} work units")
    await asyncio.sleep((crawler.worker_id - 1) * 2)  # prevents seleniumbase instances from starting at the same time
    await asyncio.to_thread(_run)


def _split_evenly(items: list[dict[str, Any]], workers: int) -> list[list[dict[str, Any]]]:
    return [items[i::workers] for i in range(workers)]


def _split_limits(total: int, workers: int) -> list[int]:
    base: int = total // workers
    remainder: int = total % workers
    return [base + (1 if i < remainder else 0) for i in range(workers)]


def _build_work_units(links: list[str], categories: list[str], workers: int) -> list[dict[str, Any]]:
    """ merge links and categories into one list for workers to split it between each other """
    work_units: list[dict[str, Any]] = []

    for link in links:
        work_units.append({
            "type": "link",
            "value": link,
        })

    if len(categories) == 1 and workers > 1:
        category = categories[0]
        for i in range(workers):
            work_units.append({
                "type": "category",
                "value": category,
                "starting_page": i + 1,
                "shard_step": workers,  # each worker gets a page to crawl without interfering with other workers
            })
    else:
        for category in categories:
            work_units.append({
                "type": "category",
                "value": category,
            })

    return work_units


def _crawl_category_shard(
        crawler: InvestingCrawler,
        done: asyncio.Event,
        topic_category: str,
        stop_date: Optional[dt.datetime] = None,
        starting_page: int = 1,
        shard_step: int = 1,
) -> Generator[Article, None, None]:
    """ crawl category with a stepping mechanism so workers don't interfere with each other's work """
    page_generator: Generator[str, None, None] = crawler.pagination(topic=topic_category, starting_page=starting_page)

    while not done.is_set():
        page_url: str = next(page_generator)

        for article in crawler.crawl_page(link=page_url, stop_date=stop_date):
            yield article

        for _ in range(shard_step - 1):  # skipping a page
            next(page_generator)


async def crawling_manager(actor, actor_input: dict[str, Any]) -> None:
    """ the crawling manager responsible for crawling preparing the system and workers for crawls """
    await charge_user(actor, 'actor-start')
    logger.info("charged user for actor start")

    rebuild_database()
    clean_processes()

    done = asyncio.Event()

    links: list[str] = actor_input.get("links") or []
    categories: list[str] = actor_input.get("categories") or []

    if categories: workers = min(settings["WORKERS"], actor_input["max_articles"])
    else: workers = min(settings["WORKERS"], len(links), actor_input["max_articles"])
    workers = max(1, workers)  # do not create more workers than the total article target (nor less)

    work_units: list[dict[str, Any]] = _build_work_units(links, categories, workers)
    if not work_units:
        logger.warning("no work units were built, crawler exiting..")
        return

    chunks: list[list[dict[str, Any]]] = _split_evenly(work_units, workers)
    limits_per_worker: list[int] = _split_limits(actor_input["max_articles"], workers)
    tasks: list[Coroutine] = [push_data(actor, actor_input, done)]
    workers_crawlers: list[InvestingCrawler] = [
        InvestingCrawler(
            worker_id=i + 1,
            proxy=(actor_input["proxy"] or None)
        )
        for i in range(workers)
    ]

    logger.info(
        f"prepared {workers} workers for {len(links)} links and {len(categories)} categories "
        f"with {len(work_units)} total work units and per-worker limits {limits_per_worker}"
    )

    for crawler, chunk, limit in zip(workers_crawlers, chunks, limits_per_worker):
        if not chunk or limit <= 0: continue

        logger.info(
            f"initiating worker {crawler.worker_id}/{workers} "
            f"with {len(chunk)} jobs and articles limit {limit}"
        )

        tasks.append(
            crawl_worker(
                crawler=crawler,
                done=done,
                work_units=chunk,
                stop_date=actor_input["stop_date"],
                max_articles_per_worker=limit,
            )
        )

    await asyncio.gather(*tasks)
