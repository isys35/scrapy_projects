import scrapy
from scrapy.http import Request


class EverythingkitchensSpiderSpider(scrapy.Spider):
    name = 'everythingkitchens_spider'
    allowed_domains = ['www.everythingkitchens.com']
    start_urls = ['https://www.everythingkitchens.com/']

    def parse(self, response):
        categories_urls = response.css('.level-top::attr(href)').getall()
        for category_url in categories_urls:
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        products_urls = response.css('a.product-item-link::attr(href)').getall()
        for product_url in products_urls:
            yield Request(product_url, callback=self.parse_product)

    def parse_product(self, response):
        upc = None
        trs = response.css('tr')
        mpn = None
        for tr in trs:
            th = tr.css('th.col.label::text').get()
            if th and th == 'GTIIN / UPC Code':
                td = tr.css('td.col.data::text').get()
                upc = td
            if th and th == 'Manufacturer Part Number':
                td = tr.css('td.col.data::text').get()
                mpn = td
        name = response.css('span.base::text').get()
        price = response.css('div.product-info-price span.price::text').get()
        if price:
            price = price.replace('$', '')
        sku = response.css('.product.attribute.sku div.value::text').get()
        yield {'GTIIN / UPC Code': upc, 'Name': name, 'Price': price,
               'SKU': sku, 'MPN': mpn, 'Link': response.url}