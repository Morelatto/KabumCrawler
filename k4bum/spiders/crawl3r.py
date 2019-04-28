import scrapy

from scrapy.loader import ItemLoader
from k4bum.items import Product


TEXT_SEL = '::text'
CATEGORIES = '.bot-categoria a'
PRODUCT_DETAILS = '//div[@class="listagem-bots"]/a'
PAGE_BAR = '.listagem-paginacao'
NEXT_PAGE = 'td:last-child a'
PROD_BRAND = '.marcas img::attr(alt)'
PROD_NAME = '.titulo_det' + TEXT_SEL
UNAVAILABLE = '.bot_comprar a'
REVIEW_COUNT = '.avaliacao meta:last-child::attr(content)'
RATING_VALUE = '.avaliacao meta:first-child::attr(content)'
STARS_COMMENTS = '.opiniao_box .H-estrelas::attr(class)'
DISCOUNT_AMOUNT = 'div.preco_desconto font' + TEXT_SEL
PRICE_DISCOUNT = 'span.preco_desconto strong' + TEXT_SEL
PRICE_REAL = '.preco_normal' + TEXT_SEL
PARCEL_TABLE = '.ParcelamentoCartao ul li *' + TEXT_SEL


class Crawl4r(scrapy.Spider):
    name = 'crawl4r'
    allowed_domains = ['k4bum.com.br']
    start_urls = ['https://www.k4bum.com.br']

    def __init__(self, category=None, *args, **kwargs):
        super(Crawl4r, self).__init__(*args, **kwargs)
        self.category = category

    def parse(self, response):
        for category in response.css(CATEGORIES):
            if self.category == category.css(TEXT_SEL).get():
                yield scrapy.Request(
                    url=response.urljoin(category.attrib['href'] + '?ordem=5&limite=100&pagina=1&string='),
                    callback=self.parse_category,
                    meta={'page': 1})

    def parse_category(self, response):
        products = response.xpath(PRODUCT_DETAILS)
        self.logger.info('Page %d - %d' % (response.meta['page'], len(products)))
        for product in products:
            yield scrapy.Request(url=product.attrib['href'], callback=self.parse_product)

        next_page = response.css(PAGE_BAR)[0].css(NEXT_PAGE)
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page.attrib['href']),
                                 callback=self.parse_category,
                                 meta={'page': response.meta['page'] + 1})

    def parse_product(self, response):
        il = ItemLoader(item=Product(), response=response)
        il.add_css('name', PROD_NAME)
        il.add_css('brand', PROD_BRAND)
        il.add_css('available', UNAVAILABLE)

        il.add_css('stars', RATING_VALUE)
        il.add_css('ratings', REVIEW_COUNT)
        il.add_css('real_stars', STARS_COMMENTS)

        il.add_css('price', PRICE_REAL)
        il.add_css('price_boleto', PRICE_DISCOUNT)
        il.add_css('discount_boleto', DISCOUNT_AMOUNT)
        il.add_css('parcel_table', PARCEL_TABLE)

        il.add_css('description', 'p[itemprop="description"]' + TEXT_SEL)
        il.add_css('tech_spec', '')
        il.add_css('warranty', '')


'''
p - description
p - barra img - ignore
commented p (barra img)
p - title - ignore


redirect auto throttle output to file
 
'''
