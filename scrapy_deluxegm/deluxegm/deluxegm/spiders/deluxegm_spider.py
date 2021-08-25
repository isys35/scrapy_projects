import scrapy
from scrapy.http import Request, FormRequest
import re

class DeluxegmProductSpider(scrapy.Spider):
    name = 'deluxegm_spider'
    allowed_domains = ['www.deluxegm.com']
    host = 'http://www.deluxegm.com'
    auth_url = 'https://www.deluxegm.com/login.jhtm'
    start_url = 'http://www.deluxegm.com/'

    def start_requests(self):
        yield FormRequest(url=self.auth_url, callback=self.parse,
                          formdata={'username': 'sales@fabiusgroup.com', 'password': 'Fabius2021#'})

    def parse(self, response):
        yield Request(self.start_url, callback=self.parse_categories_page)

    def parse_categories_page(self, response):
        categories_urls = response.css('a.dropdown-toggle.collapsed::attr(href)').getall()
        for category_href in categories_urls:
            category_url = self.host + category_href
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        details_hrefs = response.css('div.product_name a::attr(href)').getall()
        for detail_href in details_hrefs:
            detail_url = self.host + detail_href
            yield Request(detail_url, callback=self.parse_detail)
        page_nav = response.css('span.pageNavLink')
        next_url = page_nav[-1].css(' a::attr(href)').get()
        print('************')
        print(next_url)
        if next_url and next_url != '#':
            yield Request(next_url, callback=self.parse_category)

    def parse_detail(self, response):
        name = response.css('h1::text').get()
        sku = response.css('span.sku_value::text').get()
        upc_code = response.css('span.upccode_value::text').get()
        re_search_price = re.search("newprice = \'(.*)?';", response.css('body').get())
        price = None
        if re_search_price:
            price = re_search_price.group(1)
        pack_size = None
        case_pack = response.css('.casepack_value::text').get()
        colors = None
        for detail_spec in response.css('div.details_specification'):
            for row in detail_spec.css(' .clearfix'):
                spec_title = row.css(' .spec_title::text').get()
                spec_info = row.css(' .spec_info::text').get()
                if spec_title == 'Colors':
                    colors = spec_info
                if spec_title == 'Inner Case':
                    pack_size = spec_info
        description = response.css('.details_long_desc::text').get().strip()
        yield {'Name': name, 'SKU': sku, 'UPC Code': upc_code, 'price': price, 'Pack Size': pack_size,
               'Case Pack': case_pack, 'Description': description, 'Colors': colors}

