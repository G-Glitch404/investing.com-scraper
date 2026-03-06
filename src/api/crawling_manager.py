import asyncio
from typing import Any

from src.settings import settings, crawler_categories
from src.core.database import Database
from src.core.logger import Logger

logger = Logger("CrawlingManager")


def article_filter(article: dict[str, Any], actor_input: dict[str, Any]) -> tuple[bool, str]:
    """
     checks if an article is valid to push or not
     returns:
        True if article should be filtered and is invalid for user inputs - str of drop reason
        False if article is valid to user inputs - empty str (no reason to drop)
    """
    logger.debug("validating an article before pushing to user")

    # filter fields check
    for field in actor_input["filter_fields"]:
        val: str = article[field]
        if not val: return True, f"missing field {field}"
        if (isinstance(val, str) and val.strip() == "") or (isinstance(val, (list, dict)) and len(val) == 0):
            return True, f"missing field {field}"

    # categories check
    if "all" not in actor_input["categories"]:
        art_cat: str = article.get("category")
        all_cats: list[str] = crawler_categories["all_categories"] + crawler_categories["special_categories"]
        if (not art_cat) or (art_cat not in all_cats):
            return True, "article category unavailable"
        if art_cat not in actor_input["categories"]:
            return True, "category mismatch"

    # keywords check (case-sensitive per schema notes)
    if actor_input["keywords"]:
        art_text: str = article["body"]
        if not isinstance(art_text, str):
            art_text: str = article["title"] + (article["summery"] or "")

        match: bool = False
        for kw in actor_input["keywords"]:
            if kw in art_text: match = True; break
        if not match: return True, f'no keywords matched'

    return False, ""


async def push_data(actor, actor_input: dict[str, Any]) -> None:
    """ fetch the articles from the database then push them to the actor storage for user """
    counter: int = 0
    counter_prev: int = 0  # used for the timeout logic
    counter_last: int = 0  # used for the actor status message
    retries: int = 0

    logger.info('Pushing articles to Apify platform...')

    while counter < actor_input["max_articles"]:
        await asyncio.sleep(5)

        for db_article in Database().fetch_all():
            if counter >= actor_input["max_articles"]: break
            if not db_article: continue

            if authors := db_article[5]: authors = authors.split(' , ')
            if tags := db_article[10]: tags = tags.split(' , ')
            if images := db_article[13]: images = images.split(' , ')

            article = {
                # skipping database column (id)
                "Icon": db_article[1],
                "Title": db_article[2],
                "Summary": db_article[3],
                "Publisher": db_article[4],
                "Authors": authors,
                "Category": db_article[6],
                "Article Type": db_article[7],
                "Published": db_article[8],
                "Modified": db_article[9],
                "Tags": tags,
                "Body": db_article[11],
                "URL": db_article[12],
                "Images": images,
            }

            filter_status: tuple[bool, str] = article_filter(article, actor_input)
            if not filter_status[0]:
                await actor.push_data(article)
                counter += 1
            else: logger.warning(f'dropped an article - reason: "{filter_status[1]}" - article: "{article}"')

            Database(settings["DATABASE"]).delete_record(db_article[0])  # delete from db, articles can be re-fetched
            if counter >= 100 and counter_last != int(str(counter)[0]):
                await actor.set_status_message(f'scrapped {counter}/{actor_input["max_articles"]} articles please be patient...')
                logger.debug(f'articles push loop is still going (scrapped {counter}/{actor_input["max_articles"]} articles)')
            counter_last: int = int(str(counter)[0])
        # for loop end

        if counter_prev == settings["ARTICLES_FOUND"].value:
            retries += 1    # timeout logic so if the actor is not finding any articles for ~15secs it will force stop
            await asyncio.sleep(5)
            if retries >= 3:
                logger.debug('user probably got enough articles or at least all available articles forcing actor exit')
                break
        counter_prev = settings["ARTICLES_FOUND"].value


async def crawling_manager(actor, actor_input: dict) -> None:
    pass
