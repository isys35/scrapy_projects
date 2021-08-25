import scrapy
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
import time
import re


def save_html(text, file_name='page.html'):
    with open(file_name, 'w', encoding='utf-8') as html_file:
        html_file.write(text)


class BdiexpressProductSpider(scrapy.Spider):
    name = 'bdiexpress_product'
    allowed_domains = ['www.bdiexpress.com']
    host = 'https://www.bdiexpress.com'
    auth_url = 'https://www.bdiexpress.com/us/en/j_spring_security_check'
    start_url = 'https://www.bdiexpress.com/us/en/'

    def start_requests(self):
        return [Request(url="https://www.bdiexpress.com/us/en/login", callback=self.login)]

    def login(self, response):
        inputs = response.css('input')
        csrf_token = None
        for input in inputs:
            if input.css('::attr(name)').get() == 'CSRFToken':
                csrf_token = input.css('::attr(value)').get()
                break
        return scrapy.FormRequest(self.auth_url,
                                  formdata={'j_username': 'sales@fabiusgroup.com', 'j_password': 'Fabius2021#',
                                            "remember-me": 'on', 'CSRFToken': csrf_token},
                                  callback=self.parse)

    def parse(self, response):
        urls_categories_css = response.css('div.link.root a')
        for url_categorie_css in urls_categories_css:
            id = url_categorie_css.css('::attr(id)').get()
            if id:
                if 'SubCategory' in id:
                    continue
                title_categorie = url_categorie_css.css('::attr(title)').get()
                if not title_categorie:
                    continue
                if title_categorie == 'Ask us. We can help!':
                    continue
                title_categorie = title_categorie.replace(' ', '')
                url_categorie = f'https://www.bdiexpress.com/us/en/search?page=1&pageSize=5&q=&c={title_categorie}&format=json&_={int(time.time()*1000)}'
                yield Request(url_categorie, callback=self.parse_products)

    def parse_products(self, response):
        jsonresponse = response.json()
        product_html = jsonresponse.get('productHTML', '')
        hrefs_products = Selector(text=product_html).css('.plp-product-name a::attr(href)').getall()
        for href_product in hrefs_products:
            url_product = self.host + href_product
            yield Request(url_product, callback=self.parse_product)
        next_href = jsonresponse.get('nextPage')
        if next_href:
            next_url = self.host + next_href
            yield Request(next_url, callback=self.parse_products)

    def parse_product(self, response):
        specifications = response.css('div.specifications').get().replace('\t', '').replace('\n', '')
        re_search_ean = re.search(r'<div class=\"item label\">EAN</div><div class=\"item strong\">(.*?)</div>', specifications)
        if re_search_ean:
            ean = re_search_ean.group(1)
            re_search_product_detail = re.search(r'<div class=\"item label\">Product Detail</div><div class=\"item strong\">(.*?)</div>', specifications)
            if re_search_product_detail:
                product_detail = re_search_product_detail.group(1)
            else:
                product_detail = None
            re_search_manufacturer_internal_number = re.search(r'<div class=\"item label\">Manufacturer Internal Number</div><div class=\"item strong\">(.*?)</div>', specifications)
            if re_search_manufacturer_internal_number:
                manufacturer_internal_number = re_search_manufacturer_internal_number.group(1)
            else:
                manufacturer_internal_number = None
            re_search_manufacturer_name = re.search(r'<div class=\"item label\">Manufacturer Name</div><div class=\"item strong\">(.*?)</div>',specifications)
            if re_search_manufacturer_name:
                manufacturer_name = re_search_manufacturer_name.group(1)
            else:
                manufacturer_name = None
            re_search_minimum_buy_quantity = re.search(r'<div class=\"item label\">Minimum Buy Quantity</div><div class=\"item strong\">(.*?)</div>', specifications)
            if re_search_minimum_buy_quantity:
                minimum_buy_quantity = re_search_minimum_buy_quantity.group(1)
            else:
                minimum_buy_quantity = None
            price = response.css('span.price-list span#PDP_Price.price.notransform::text').get()
            if price:
                price = price.strip()
            # if price:
            #     re_search_price = re.search(r'\$ (.*) / each', price)
            #     if re_search_price:
            #         price = re_search_price.group(1)
            yield {'EAN  (UPC)': ean, 'Product Detail': product_detail,
                   'Manufacturer Internal Number': manufacturer_internal_number,
                   'Manufacturer Name': manufacturer_name, 'Price': price, 'Minimum Buy Quantity':minimum_buy_quantity, 'Link': response.url}
