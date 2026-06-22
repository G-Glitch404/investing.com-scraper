from src.crawler.investing_crawler import InvestingCrawler

max_articles: int = 10
categories: list[str] = ["latest-news"]
links: list[str] = ["https://www.investing.com/news/latest-news/1"]


def test_scrape_links() -> None:
    crawler = InvestingCrawler()
    articles_counter: int = 0
    for link in links:
        if articles_counter >= max_articles: break
        for article in crawler.crawl_page(link=link):
            if articles_counter >= max_articles: break
            articles_counter += 1

            for k, v in article:
                print(f"{k}: {v}")

    assert articles_counter == max_articles


def test_scrape_categories() -> None:
    crawler = InvestingCrawler()
    articles_counter: int = 0
    for category in categories:
        if articles_counter >= max_articles: break
        for article in crawler.crawl(topic_category=category, max_articles=max_articles):
            if articles_counter >= max_articles: break
            articles_counter += 1

            for k, v in article:
                print(f"{k}: {v}")

    assert articles_counter == max_articles
