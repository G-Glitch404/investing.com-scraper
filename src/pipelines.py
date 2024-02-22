from scrapy.exceptions import DropItem, CloseSpider
from scrapy import Item, Spider
from scrapy.selector import Selector
from itemadapter import ItemAdapter
import apify.actor
import apify.scrapy.pipelines

import datetime
import re


class InvestingSpiderPipeline:
    def __init__(self, allowed_date_range):
        self.drops_counter = 0
        self.today = datetime.datetime.today().date()
        self.months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        self.allowed_date_range = allowed_date_range

    @classmethod
    def from_crawler(cls, crawler):
        allowed_date_range = crawler.settings.get('ALLOWED_DATE_RANGE')
        return cls(allowed_date_range)

    def process_item(self, item, spider):
        spider.logger.info(f'Processing item link: {item["link"]}')
        if self.drops_counter >= 150:
            raise CloseSpider(f"[DropLimit] Drop limit reached: {self.drops_counter} drops")
        else:
            article_date = item['date'][0].replace(',', '').lower().split(' ')[1:4]
            article_date = datetime.date(int(article_date[2]), self.months.index(article_date[0]) + 1, int(article_date[1]))  # YYYY/M/D
            try:
                spider.logger.info(f'Processing item date: {self.allowed_date_range}')
                if self.allowed_date_range:
                    if self.allowed_date_range != 'anytime':
                        self.__is_allowed_date(item['link'], article_date, self.allowed_date_range)
                else:
                    if article_date != self.today:
                        raise DropItem(f"item {item['link']} not from today's date")
            except DropItem as e:
                self.drops_counter += 1
                raise DropItem(e)
            else:
                self.drops_counter = 0

            item['comments'][0] = int(item['comments'][0])
            if item['comments'][0] > 0:
                item['comments'][1] = [
                    [
                        f"{title}",  # name
                        f"{comment.css('span.js-date ::attr(comment-date)').get().replace('{dateFormat}', '')}",  # date
                        f"{comment.css('span.js-text ::text').get()}",  # body
                        f"https://www.investing.com{comment.css('a.js-user-link::attr(href)').get()}",  # profile_url
                    ]
                    for comment in item['comments'][1] if (
                        title := comment.css('a.js-user-link > img ::attr(alt)').get().replace('{usernameAlt}', '')) != ''
                ]
            else:
                item['comments'] = [0, None]

            if '</script>' in (p := item['paragraph'].get()):
                paragraphs = []
                for paragraph in Selector(text=p.split('</script>')[-1], type="html").css('::text').extract():
                    if 'InvestingPro' in paragraph: break
                    paragraphs.append(paragraph)
                item['paragraph'] = re.sub(r"\n{2,}", "\n", ''.join(paragraphs).strip())
            else:
                item['paragraph'] = re.sub(r"\n{2,}", "\n", ''.join(item['paragraph'].css('::text').extract()).strip())

            item['date'] = [f"{date}" for date in item['date']] if len(item['date']) > 1 else item['date'][0] or None
            item['publisher'] = item['publisher'].replace('By ', '')
            item['category'] = item['category'].split("/news/", 1)[-1].replace("-", ' ').split('/', 1)[0].strip().capitalize()

            return item

    def __is_allowed_date(self,
                          item: str,
                          article_date: datetime.date,
                          allowed_date_range: tuple[datetime.date, datetime.date] | datetime.date) -> bool:

        if type(allowed_date_range) is tuple:
            if allowed_date_range[0] == self.today:
                if allowed_date_range[0] > article_date:
                    raise DropItem(f"dropped item #{item} date {article_date} not in requested date range {allowed_date_range}")
            elif allowed_date_range[0] < article_date < allowed_date_range[1]:
                raise DropItem(f"dropped item #{item} date {article_date} not in requested date range {allowed_date_range}")
        elif type(allowed_date_range) is datetime.date:
            if allowed_date_range != article_date:
                raise DropItem(f"dropped item #{item} date {article_date} not in requested date range {allowed_date_range}")
        else:
            raise CloseSpider(f"{allowed_date_range} date requested is malformed can't be processed")

        return True


class ActorPushPipeline(apify.scrapy.pipelines.ActorDatasetPushPipeline):
    def __init__(self, item_count):
        self.item_count = item_count
        self.counter = 0

    @classmethod
    def from_crawler(cls, crawler):
        item_count = crawler.settings.get('CLOSESPIDER_ITEMCOUNT')
        return cls(item_count)

    async def process_item(self, item: Item, spider: Spider) -> None:
        """Pushes the provided Scrapy item to the Actor's default dataset."""
        self.counter += 1
        if self.counter <= self.item_count:
            item_dict = ItemAdapter(item).asdict()
            await apify.actor.Actor.push_data(item_dict)
            spider.logger.info(f'item #{self.counter} pushed to the dataset.')
