import scrapy
from scrapy.http import Request
import re


def parse_meta_by_name(response, name):
    metas = response.css('meta')
    for meta in metas:
        name_meta = meta.css('::attr(name)').get()
        if name_meta == name:
            return meta.css('::attr(content)').get()


class WasserstromSpiderSpider(scrapy.Spider):
    name = 'wasserstrom_spider'
    allowed_domains = ['www.wasserstrom.com']
    _pre_url = 'https://www.wasserstrom.com/restaurant-supplies-equipment/'
    start_urls = ['https://www.wasserstrom.com/restaurant-supplies-equipment/shop-all-categories']

    def parse(self, response):
        categories_hrefs = response.css('div.wasserstrom-shop-all-categories-gallery a::attr(href)').getall()
        for category_href in categories_hrefs:
            category_url = self._pre_url + category_href
            yield Request(category_url, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        subcategory_hrefs = response.css(
            '.catPos.categorySpot div.container a.product_group_name.product_info::attr(href)').getall()
        for subcategory_url in subcategory_hrefs:
            yield Request(subcategory_url, callback=self.parse_category)

    def parse_category(self, response):
        subcategory_hrefs = response.css(
            '.catPos.categorySpot div.container a.product_group_name.product_info::attr(href)')
        if subcategory_hrefs:
            yield Request(response.url, callback=self.parse_category)
        product_hrefs = response.css('div.product_name a::attr(href)').getall()
        for product_url in product_hrefs:
            yield Request(product_url, callback=self.parse_product)
        if not response.css('.right_arrow.invisible') and product_hrefs:
            page_id = response.meta.get('page_id') or parse_meta_by_name(response, 'pageId')
            begin_index = response.meta.get('begin_index') or 0
            begin_index += 20
            url = f'https://www.wasserstrom.com/restaurant-supplies-equipment/WassProductListingView?top_category2=&top_category3=&facet=&searchTermScope=&top_category4=&top_category5=&searchType=&filterFacet=&resultCatEntryType=&sType=SimpleSearch&top_category=&gridPosition=&ddkey=ProductListingView_6_3074457345618260656_3074457345618312070&metaData=&ajaxStoreImageDir=/wcsstore/WasserstromStorefrontAssetStore/&advancedSearch=&categoryId={page_id}&categoryFacetHierarchyPath=&searchTerm=&emsName=Widget_WASSCatalogEntryListWidget_3074457345618312070&filterTerm=&manufacturer=&resultsPerPage=20&disableProductCompare=false&parent_category_rn=&catalogId=3074457345616677089&langId=-1&enableSKUListView=false&storeId=10051'
            body = f'contentBeginIndex=0&productBeginIndex={begin_index}&beginIndex={begin_index}&orderBy=&facetId=&pageView=grid&resultType=both&orderByContent=&searchTerm=&facet=&facetLimit=&minPrice=&maxPrice=&pageSize=&catalogMode=&storeId=10051&catalogId=3074457345616677089&langId=-1&homePageURL=https%3A%2F%2Fwww.wasserstrom.com&commandContextCurrency=USD&enableSKUListView=&widgetPrefix=6_3074457345618312070&pgl_widgetId=3074457345618312070&objectId=_6_3074457345618260656_3074457345618312070&requesttype=ajax'
            request = Request(url, method='POST', body=body, callback=self.parse_category)
            request.meta['begin_index'] = begin_index
            request.meta['page_id'] = page_id
            yield request

    def parse_product(self, response):
        info_rows = response.css('div.row.row_border')
        upc = None
        for info_row in info_rows:
            head = info_row.css('div.heading::text')
            if head and head.get().strip() == 'UPC':
                upc = info_row.css('div.item::text').get().strip()
                break
        name = response.css('h1.main_header::text').get().strip()
        price = response.css('.price::text')
        if price:
            price = price.get().strip().replace('$', '')
        page_str = str(response.css('body').get())
        item_number = re.search('<strong>Item #:</strong>(.+?)</span>', page_str)
        if item_number:
            item_number = item_number.group(1).strip()
        model = re.search('<strong>Model #:</strong>(.+?)</span>', page_str)
        if model:
            model = model.group(1).strip()
        manufacter = re.search('<strong>Manufacturer:</strong>(.+?)</span>', page_str)
        if manufacter:
            manufacter = manufacter.group(1).strip()
        if not manufacter:
            manufacter = response.css('a#manufacturerInfoSubCategoryLink::text')
            if manufacter:
                manufacter = manufacter.get().strip()
        if upc:
            yield {'UPC:': upc,
                   'Name:': name,
                   'Price:': price,
                   'Item #:': item_number,
                   'Model #:': model,
                   'Manufacturer:': manufacter,
                   'Link:': response.url}
