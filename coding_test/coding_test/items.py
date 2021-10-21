# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CodingTestItem(scrapy.Item):
    # define the fields for your item here like:
    item_id = scrapy.Field()
    name = scrapy.Field()
    image_id = scrapy.Field()
    flavor  = scrapy.Field()
    pass
