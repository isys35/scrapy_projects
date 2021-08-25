import scrapy
from scrapy import Request
import re


class BuktoystoreSpider(scrapy.Spider):
    name = 'buktoystore'
    allowed_domains = ['bulktoystore.com']
    start_urls = ['https://bulktoystore.com/']
    host = 'https://bulktoystore.com'

    def parse(self, response):
        for href_category in response.css('a.top_link::attr(href)').getall():
            url = self.host + href_category
            yield Request(url, callback=self.parse_category)

    def parse_category(self, response):
        products_hrefs = response.css('a.product-info__caption::attr(href)').getall()
        for product_href in products_hrefs:
            product_url = self.host + product_href
            yield Request(product_url, callback=self.parse_product)
        next_page_href = response.css('span.next a::attr(href)').get()
        if next_page_href:
            next_page_url = self.host + next_page_href
            yield Request(next_page_url, callback=self.parse_category)

    def parse_product(self, response):
        head = response.css('head').get()
        re_search_upc = re.search(r'"productId":"(.*?)"', head)
        upc = None
        if re_search_upc:
            upc = re_search_upc.group(1)
        name = response.css('h1::text').get()
        price = None
        re_search_price = re.search(r'"price":"(.*?)"', head)
        if re_search_price:
            price = re_search_price.group(1)
        sku = None
        re_search_sku = re.search(r'"sku":"(.*?)"', head)
        if re_search_sku:
            sku = re_search_sku.group(1)
        if upc:
            yield {'UPC': upc, 'Name': name, 'Price': price,
                   'SKU': sku, 'Link': response.url}
