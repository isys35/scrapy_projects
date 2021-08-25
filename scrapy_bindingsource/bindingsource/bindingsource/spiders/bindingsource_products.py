import scrapy
from scrapy.http import HtmlResponse
from bindingsource.items import Product


class BindingsourceProductsSpider(scrapy.Spider):
    name = 'bindingsource_products'
    host = 'https://bindingsource.com/'
    allowed_domains = ['bindingsource.com']
    start_urls = ['https://bindingsource.com/']

    def parse(self, response: HtmlResponse):
        menu_items = response.css('.category-menu li.navPages-item')
        for menu_item in menu_items:
            url = menu_item.css('a::attr(href)').get()
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response: HtmlResponse):
        titles = response.css('h4.card-title')
        for title in titles:
            product_url = title.css('a::attr(href)').get()
            yield scrapy.Request(product_url, callback=self.parse_product)
        next_page = response.css('li.pagination-item.pagination-item--next')
        if next_page:
            next_page_url = next_page.css('a::attr(href)').get()
            yield scrapy.Request(next_page_url, callback=self.parse_category)

    def parse_product(self, response: HtmlResponse):
        item = Product()
        item['name'] = response.css('h1.productView-title::text').get()
        detail_list = response.css('ul.details-list').css('li')
        for detail in detail_list:
            if detail.css('.productView-info-name::text').get() == 'SKU:':
                item['sku'] = detail.css('.productView-info-value::text').get()
            elif detail.css('.productView-info-name::text').get() == 'UPC:':
                item['upc'] = detail.css('.productView-info-value::text').get()
            elif detail.css('.productView-info-name::text').get() == 'Unit of Measure:':
                item['unit_of_measure'] = detail.css('.productView-info-value::text').get()
        item['price'] = response.xpath("//meta[@itemprop='price']/@content").get()
        item['minimum_purchasable_quantity'] = response.xpath("//input[@name='qty[]']/@data-interval").get()
        item['url'] = response.url
        item['category'] = response.css('a.breadcrumb-label::text')[-2].get()
        yield item
