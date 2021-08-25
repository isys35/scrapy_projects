import scrapy
from scrapy.http import Request


class BargainwSpiderSpider(scrapy.Spider):
    name = 'bargainw_spider'
    allowed_domains = ['www.bargainw.com']
    start_urls = ['http://www.bargainw.com/']
    host = 'http://www.bargainw.com'

    def parse(self, response):
        categories_hrefs = response.css('p.seeAll::attr(data-link)').getall()
        for category_href in categories_hrefs:
            if category_href.startswith('http'):
                category_url = category_href
            else:
                category_url = self.host + category_href
            yield Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        products_hrefs = response.css('div.product_name a::attr(href)').getall()
        for product_href in products_hrefs:
            if product_href.startswith('http'):
                product_url = product_href
            else:
                product_url = self.host + product_href
            yield Request(product_url, callback=self.parse_product)
        next_page = response.css('a.pageNavLink.pageNavNext::attr(href)').get()
        if next_page:
            if not next_page.startswith('http'):
                next_page = self.host + next_page
            yield Request(next_page, callback=self.parse_category)

    def parse_product(self, response):
        upc = response.css('span.upc_value::text').get()
        name = response.css('div.details_cateory_name::text').get()
        if name:
            name = name.strip()
        table_price = response.css('table.mb-30')[1]
        price_each = table_price.css('td.pv-5.pr-30 span.price_value::text').get()
        if price_each:
            price_each = price_each.replace('$', '').strip()
        price_case = table_price.css('td.pv-5.pl-30 span.price_value::text').get()
        if price_case:
            price_case = price_case.replace('$', '').strip()
        table_head = response.css('table.mb-30')[0]
        case_pack = response.css('span.casepack_value::text').get()
        sku = table_head.css('td.pv-5.pr-30::text').get()
        if sku:
            sku = sku.replace('Артикул# ', '').strip()
            sku = sku.replace('Sku# ', '')
        system_name = None
        details_info_table = response.css('div.details_specification .clearfix')
        for row in details_info_table:
            title = row.css('div.spec_title::text').get()
            if title:
                if title.strip() == 'System Name':
                    system_name = row.css('div.spec_info::text').get()
                    if system_name:
                        system_name = system_name.strip()
        yield {'UPC No': upc, 'Name': name, 'Price each': price_each, 'Price case': price_case,
               'Case pack': case_pack, 'SKU': sku, 'System Name': system_name, 'Link': response.url}
