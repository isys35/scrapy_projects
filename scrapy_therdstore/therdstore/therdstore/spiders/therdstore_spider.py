import scrapy
import re
from scrapy.http import Request, FormRequest


class TherdstoreSpiderSpider(scrapy.Spider):
    name = 'therdstore_spider'
    allowed_domains = ['www.therdstore.com', 'therds.a.searchspring.io']
    api_url = 'https://therds.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=therds&domain={}&bgfilter.catcode={}&q=&page={}'

    def start_requests(self):
        return [FormRequest('https://www.therdstore.com/',
                            formdata={'Action': 'LOGN',
                                      'Customer_LoginEmail': 'sales@fabiusgroup.com',
                                      'Customer_Password': 'Fabius2021#'},
                            callback=self.parse)]

    def parse(self, response):
        categories = response.css("a.x-omega-navigation__grandchild-link::attr(href)").getall()
        for category in categories:
            yield Request(category, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        subcategories = response.css("a.u-block.u-color-black.t-subcategory-navigation__link::attr(href)").getall()
        if subcategories:
            for subcategory in subcategories:
                yield Request(subcategory, callback=self.parse_catcode)
        else:
            self.parse_catcode(response)

    def parse_catcode(self, response):
        catcode_search = re.search(r'catcode="(.*?)"', response.css('html').get())
        if catcode_search:
            url_products = self.api_url.format(response.url, catcode_search.group(1), 1)
            yield Request(url_products, callback=self.parse_products)

    def parse_products(self, response):
        products_json = response.json()
        for product in products_json['results']:
            product_url = 'https:' + product['url']
            yield Request(product_url, callback=self.parse_product)
        if products_json['pagination']['nextPage'] != 0:
            next_page_number = products_json['pagination']['nextPage']
            this_page_number = products_json['pagination']['currentPage']
            next_url = response.url.replace('page={}'.format(this_page_number), 'page={}'.format(next_page_number))
            yield Request(next_url, callback=self.parse_products)

    def parse_product(self, response):
        upc = response.css('#prod_upc::text').get()
        price = response.css('#js-price-value::attr(data-base-price)').get()
        additional_info = response.css('#js-price-value span::text').get()
        name = response.css('h1 span')[1].css('::text').get()
        sku = response.css('span.x-product-layout-purchase__sku::text').get()
        if sku:
            sku = sku.replace('SKU: ', '').strip()
        if additional_info:
            additional_info = additional_info.replace('/ ', '').strip()
        if upc:
            yield {"UPC": upc,
                   'Price': price,
                   'Additional info': additional_info,
                   'Name': name,
                   'Product SKU': sku,
                   'Link': response.url}
