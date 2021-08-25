# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    sku = scrapy.Field()
    upc = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    minimum_purchasable_quantity = scrapy.Field()
    unit_of_measure = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()

