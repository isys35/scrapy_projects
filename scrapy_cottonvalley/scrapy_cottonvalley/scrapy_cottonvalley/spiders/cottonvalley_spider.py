import scrapy
from scrapy.http import Request
import re


class CottonvalleySpiderSpider(scrapy.Spider):
    name = 'cottonvalley_spider'
    allowed_domains = ['www.cottonvalley.net']
    start_urls = ['https://www.cottonvalley.net/shop/']

    def parse(self, response):
        products_urls = response.css('.woocommerce-loop-product__link::attr(href)').getall()
        for product_url in products_urls:
            yield Request(product_url, callback=self.parse_product)
        next_page_url = response.css('a.next.page-numbers::attr(href)').get()
        if next_page_url:
            yield Request(next_page_url, callback=self.parse)

    def parse_product(self, response):
        name = response.css('h1::text').get()
        sku = response.css('span.sku::text').get()
        scripts = '\n'.join(response.css('script').getall())
        description = response.css('#tab-description').get()
        price = None
        re_search_price = re.search('"price":"(.*?)",', scripts)
        if re_search_price:
            price = re_search_price.group(1)
        master_case_pack = None
        re_search_master_case_pack = re.search('Master Case Pack: (\d+)', description)
        if re_search_master_case_pack:
            master_case_pack = re_search_master_case_pack.group(1)
        price_per_one_piece = None
        re_search_price_per_one_piece = re.search('\(\$ (.*?) EA\)', response.css('span.uom::text').get())
        if re_search_price_per_one_piece:
            price_per_one_piece = re_search_price_per_one_piece.group(1)
        link = response.url
        upc = None
        re_search_upc = re.search('Item UPC Code: (\d+)', description)
        if re_search_upc:
            upc = re_search_upc.group(1)
        yield {'Item UPC Code': upc, 'Name': name, 'SKU': sku, 'Price': price, 'Master Case Pack': master_case_pack,
               'Price per 1 Piece': price_per_one_piece, 'Link': link}
