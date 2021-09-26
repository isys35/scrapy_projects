import scrapy
from scrapy.http import FormRequest, Request
import re


class UpdincSpiderSpider(scrapy.Spider):
    name = 'updinc_spider'
    allowed_domains = ['www.updinc.net']
    auth_url = 'https://www.updinc.net/accounts/signin/'
    host = 'https://www.updinc.net'
    start_urls = ['https://www.updinc.net/']

    def start_requests(self):
        return [FormRequest(url=self.auth_url,
                            formdata={'username': 'sales@fabiusgroup.com',
                                      'password': 'Fabius2021#',
                                      "Action": 'Login'},
                            callback=self.parse)]

    def parse(self, response):
        hrefs = response.css('a.nav-left-li::attr(href)').getall()
        for href in hrefs:
            if not 'catid' in href:
                continue
            url = self.host + href
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        hrefs = response.css('h2 a::attr(href)').getall()
        for href in hrefs:
            url = self.host + href
            yield Request(url=url, callback=self.parse_product)
        re_url = re.search(r'\?catid=(\d+)&pageNum=(\d+)', response.url)
        category_id = int(re_url.group(1))
        page = int(re_url.group(2))
        next_page = page + 1
        url_href = '/catalog/?catid={}&pageNum={}'.format(category_id, next_page)
        all_a = response.css('a::attr(href)').getall()
        for a in all_a:
            if url_href == a:
                yield Request(url=self.host + a, callback=self.parse_category)

    def parse_product(self, response):
        prd_box_3 = str(response.css('.prdct-box3').get())
        upc = None
        upc_re = re.search(r'<strong>UPC:</strong> (.+?)<br>', prd_box_3)
        if upc_re:
            upc = upc_re.group(1).strip()
        name = response.css('h1::text').get().strip()
        dirty_price = response.css('span.notice::text').get()
        price_re = re.search('\$(.+?) ', str(dirty_price))
        price = None
        if price_re:
            price = price_re.group(1).strip()
        prd_box_2 = str(response.css('.prdct-box2').get())
        item_re = re.search(r'<strong>Item:</strong> (.+?)<br>', prd_box_2)
        item = None
        if item_re:
            item = item_re.group(1).strip()
        yield {'UPC:': upc, 'Name:': name, 'Price:': price, 'Item:': item, 'Link:': response.url}
