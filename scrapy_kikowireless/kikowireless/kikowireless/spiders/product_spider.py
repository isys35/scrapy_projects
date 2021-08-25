import scrapy
from scrapy.http import Request, FormRequest
import re


class ProductSpiderSpider(scrapy.Spider):
    name = 'product_spider'
    allowed_domains = ['www.kikowireless.com']
    auth_url = 'https://www.kikowireless.com/login'
    start_url = 'https://www.kikowireless.com/all-categories'

    def start_requests(self):
        yield FormRequest(url=self.auth_url, callback=self.parse,
                          formdata={'email': 'sales@fabiusgroup.com', 'password': 'Fabius2021#'})

    def parse(self, response):
        yield Request(self.start_url, callback=self.parse_categories_page)

    def parse_categories_page(self, response):
        categories_urls = response.css('div.product-details a::attr(href)').getall()
        for category_url in categories_urls:
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        details_urls = response.css('div.name a::attr(href)').getall()
        for detail_url in details_urls:
            yield Request(detail_url, callback=self.parse_detail)
        paginations_links = response.css('div.links a')
        url_next_page = None
        for pagination_link in paginations_links:
            if pagination_link.css('::text').get() == '>':
                url_next_page = pagination_link.css('::attr(href)').get()
                break
        if url_next_page:
            yield Request(url_next_page, callback=self.parse_category)

    def parse_detail(self, response):
        upc = response.css('div.test::text').get()
        if upc:
            upc = upc.replace('UPC: ', '').strip()
            name = response.css('h1.heading-title::text').get()
            sku = None
            for span in response.css('span.p-model'):
                if span.css('::attr(itemprop)').get() == 'model':
                    sku = span.css('::text').get()
                    break
            aviability = response.css('span.journal-stock::text').get()
            data = {'UPC': upc, 'Name': name, 'Product Model (SKU)': sku, 'Availability': aviability,
                    'Link to the product': response.url}
            discount = response.css('div.discount').get()
            price_3 = None
            price_6 = None
            price_12 = None
            if re.search('3 or more \$(\d+\.\d+)', discount):
                price_3 = re.search('3 or more \$(\d+\.\d+)', discount).group(1)
            if re.search('6 or more \$(\d+\.\d+)', discount):
                price_6 = re.search('6 or more \$(\d+\.\d+)', discount).group(1)
            if re.search('12 or more \$(\d+\.\d+)', discount):
                price_12 = re.search('12 or more \$(\d+\.\d+)', discount).group(1)
            data['Price (3 or more)'] = price_3
            data['Price (6 or more)'] = price_6
            data['Price (12 or more)'] = price_12
            yield data
