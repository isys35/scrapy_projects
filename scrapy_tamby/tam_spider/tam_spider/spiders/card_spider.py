import scrapy
import re


def load_urls_from_file():
    with open('urls', 'r', encoding='utf-8') as urls_file:
        return urls_file.read().split('\n')


class CardSpiderSpider(scrapy.Spider):
    name = 'card_spider'
    allowed_domains = ['tam.by']
    start_urls = load_urls_from_file()

    def parse(self, response):
        urls = response.css('a.tam-card-whole-link::attr(href)').getall()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_detail)
        next_page_url = response.css('li.p-next a.p-inside::attr(href)').get()
        if next_page_url:
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_detail(self, response):
        url = response.url
        rubric = response.css('a.breadcrumbs__link span::text')[-1].get()
        name = response.css('h1.section-title.company_head::text').get()
        address = response.css('a.company-card-list-link::text').get()
        metas = response.css('meta')
        phone = None
        city = None
        street = None
        for meta in metas:
            if meta.css('::attr(itemprop)').get() == 'telephone':
                phone = meta.css('::attr(content)').get()
            elif meta.css('::attr(itemprop)').get() == 'addressLocality':
                city = meta.css('::attr(content)').get()
            elif meta.css('::attr(itemprop)').get() == 'streetAddress':
                street = meta.css('::attr(content)').get()
        if city and street:
            address = '{}, {}'.format(city, street)
        social = []
        card_list_items = response.css('.company-card-list-item')
        for el in card_list_items:
            if el.css('.company-card-list-link::attr(data-type)').get() == 'social':
                re_search = re.search(r"window.open\('(.*?)',", el.css('div::attr(onclick)').get())
                if re_search:
                    social.append(re_search.group(1))
        if social:
            social = '; '.join(social)
        yield {'url': url, 'rubric': rubric, 'name': name, 'address': address, 'phone': phone,
               'social': social}
