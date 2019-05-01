import scrapy

from k4bum.items import ProductLoader

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'
PRODUCT_CATEGORIES = '.bot-categoria a'
PRODUCT_DETAILS = '.listagem-bots > a'
NEXT_PAGE = '.listagem-paginacao a'
PROD_NAME = '.titulo_det' + TEXT_SEL
PROD_BRAND = 'meta[itemprop="brand"]' + ATTR_SEL % 'content'
PROD_STARS = 'meta[itemprop="ratingValue"]' + ATTR_SEL % 'content'
PROD_REVIEWS = 'meta[itemprop="reviewCount"]' + ATTR_SEL % 'content'
PROD_COMMENTS = '.opiniao_box .H-estrelas' + ATTR_SEL % 'class'
PROD_PRICE = '.preco_normal' + TEXT_SEL
PROD_PRICE_2 = 'span.preco_desconto strong' + TEXT_SEL
PROD_DISCOUNT = 'div.preco_desconto font' + TEXT_SEL
PARCEL_TABLE = '.ParcelamentoCartao ul *' + TEXT_SEL
PROD_DESC = 'p[itemprop="description"]' + TEXT_SEL
PROD_SPEC_TABLE = '.content_tab:nth-child(2)'


class Crawl4r(scrapy.Spider):
    name = 'crawl4r'
    allowed_domains = ['k4bum.com.br']
    start_urls = ['https://www.k4bum.com.br']

    def __init__(self, cats=None, *args, **kwargs):
        super(Crawl4r, self).__init__(*args, **kwargs)
        if cats:
            self.cats = set(cats.split(','))

    def parse(self, response):
        all_cats = response.css(PRODUCT_CATEGORIES)
        for cat in all_cats:
            title = cat.css(TEXT_SEL).get()
            if title in self.cats:
                yield scrapy.Request(response.urljoin(cat.attrib['href'] + '?ordem=5&limite=100&pagina=1&string='),
                                     self.parse_product_list, meta={'cat': title})

    def parse_product_list(self, response):
        for product in response.css(PRODUCT_DETAILS):
            yield scrapy.Request(product.attrib['href'], self.parse_product,
                                 meta={'id': product.attrib['data-id'], 'cat': response.meta['cat']})

        for url in response.css(NEXT_PAGE):
            yield scrapy.Request(response.urljoin(url.attrib['href']), self.parse_product_list,
                                 meta={'cat': response.meta['cat']})

    def parse_product(self, response):
        pl = ProductLoader(response=response)
        pl.add_value('id', response.meta['id'])
        pl.add_css('name', PROD_NAME)
        pl.add_css('brand', PROD_BRAND)
        pl.add_value('category', response.meta['cat'])

        pl.add_css('stars', PROD_STARS)
        pl.add_css('ratings', PROD_REVIEWS)
        pl.add_css('comment_table', PROD_COMMENTS)

        pl.add_css('price', PROD_PRICE)
        pl.add_css('price_boleto', PROD_PRICE_2)
        pl.add_css('discount_boleto', PROD_DISCOUNT)
        pl.add_value('parcel_table', response.css(PARCEL_TABLE).getall())

        pl.add_css('description', PROD_DESC)
        pl.add_css('tech_spec', PROD_SPEC_TABLE + ' p *' + TEXT_SEL)
        pl.add_css('warranty', PROD_SPEC_TABLE + TEXT_SEL)

        yield pl.load_item()
