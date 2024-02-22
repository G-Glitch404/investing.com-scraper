import scrapy
from src.items import InvestingNewsItem


class InvestingscraperSpider(scrapy.Spider):
    # can scrape 1000 in 190 seconds for date range "anytime"

    name = "InvestingScraper"
    allowed_domains = ["www.investing.com"]

    def start_requests(self):
        for url in self.settings.get('START_URLS', None):
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        self.logger.info("Crawling: %s", response.url)

        for link in response.css('div.largeTitle > article > a.img ::attr(href)').getall():
            if '/news/' in link:
                try: publisher = response.css('span.articleDetails > span ::text').get().split('-')[0].strip()
                except IndexError: publisher = None

                yield response.follow(
                        'https://www.investing.com' + link,
                        callback=self.parse_articles,
                        cb_kwargs={'publishing_agency': publisher}
                    )

        if self.settings.get('ALLOWED_DATE_RANGE', None) is not None:
            if next_page_btn := response.css('#paginationWrap > div:nth-child(3) > a ::attr(href)').get():
                yield response.follow('https://www.investing.com' + next_page_btn, callback=self.parse)

    @staticmethod
    def parse_articles(response, publishing_agency):
        item = InvestingNewsItem()

        item["image"] = response.css('div.imgCarousel > img ::attr(src)').get()
        item["title"] = response.css('h1.articleHeader ::text').get()
        item["category"] = response.url
        item["publisher"] = publishing_agency
        item["date"] = response.css('div.contentSectionDetails > span ::text').extract() or None
        item["comments"] = [f"{response.css('span.js-counter ::text').get() or 0}", response.css('div.commentInnerWrapper')]  # comment section
        item["link"] = response.url
        item["paragraph"] = response.css('#leftColumn > div:nth-child(8)')

        yield item
