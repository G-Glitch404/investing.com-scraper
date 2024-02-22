import scrapy


class InvestingNewsItem(scrapy.Item):
    image = scrapy.Field(serializer=str)
    title = scrapy.Field(required=True, serializer=str)
    category = scrapy.Field(serializer=str)
    publisher = scrapy.Field(serialize=str)
    date = scrapy.Field(required=True)
    comments = scrapy.Field(default=None)
    link = scrapy.Field(required=True, serializer=str)
    paragraph = scrapy.Field(required=True, serializer=str)
