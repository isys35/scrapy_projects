import scrapy
from scrapy.http import Request, FormRequest
import re


class ProductSpiderSpider(scrapy.Spider):
    name = 'product_spider'
    allowed_domains = ['www.empirediscount.net']
    auth_url = 'https://www.empirediscount.net/login.php?action=check_login'
    start_url = 'https://www.empirediscount.net'

    def start_requests(self):
        return [Request(url="https://www.empirediscount.net/login.php", callback=self.login)]

    def login(self, response):
        head = response.css('head').get()
        csrf_token = re.search(r'var BCData = \{\"csrf_token":"(.+?)\"\};', head).group(1)
        return scrapy.FormRequest(self.auth_url,
                                  formdata={'login_email': 'sales@fabiusgroup.com', 'login_pass': 'Fabius2021#',
                                            "authenticity_token": csrf_token},
                                  callback=self.parse)

    def parse(self, response):
        yield Request(self.start_url, callback=self.parse_categories)

    def parse_categories(self, response):
        categories_urls = response.css('nav.navList.navList--aside li.navPages-item a::attr(href)').getall()
        categories_urls = list(set(categories_urls))
        for category_url in categories_urls:
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        details_urls = response.css('h4.card-title a::attr(href)').getall()
        for detail_url in details_urls:
            yield Request(detail_url, callback=self.parse_detail)
        url_next_page = response.css('li.pagination-item.pagination-item--next a::attr(href)').get()
        if url_next_page:
            yield Request(url_next_page, callback=self.parse_category)

    def parse_detail(self, response):
        price_view = response.css('div.productView-price')
        meta_price = price_view.css('meta')
        price = None
        for meta in meta_price:
            if meta.css('::attr(itemprop)').get() == 'price':
                price = meta.css('::attr(content)').get()
                break
        upc = response.css('dd.productView-info-value.productView-info-value--upc::text').get()
        name = response.css('h1.productView-title::text').get()
        sku = response.css('dd.productView-info-value.productView-info-value--sku::text').get()
        aviability = None
        spans = response.css('span')
        for span in spans:
            if re.search('data-product-stock', span.get()):
                aviability = span.css('::text').get()
                break
        if upc:
            yield {'UPC': upc, 'Name': name, 'Product Model (SKU)': sku, 'Price': price, 'Availability': aviability,
                   'Link to the product': response.url}
