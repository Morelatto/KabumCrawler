import scrapy

from k4bum.items import ProductLoader, PricesLoader, OfferLoader

TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'
# prod list
PRODUCT_CATEGORIES = '.bot-categoria a'
PRODUCT_DETAILS = '.listagem-bots > a'
NEXT_PAGE = '.listagem-paginacao a'
# prod
PROD_NAME = '.titulo_det' + TEXT_SEL
PROD_BRAND = 'meta[itemprop="brand"]' + ATTR_SEL % 'content'
PROD_STARS = 'meta[itemprop="ratingValue"]' + ATTR_SEL % 'content'
PROD_REVIEWS = 'meta[itemprop="reviewCount"]' + ATTR_SEL % 'content'
PROD_COMMENTS = '.opiniao_box .H-estrelas' + ATTR_SEL % 'class'
PROD_DESC = 'p[itemprop="description"]' + TEXT_SEL
PROD_SPEC_TABLE = '.content_tab:nth-child(2)'
# prices
PROD_PRICE = '.preco_normal' + TEXT_SEL
PROD_PRICE_OFFER = '.preco_desconto-cm *' + TEXT_SEL
PROD_PRICE_BOLETO = '.preco_desconto strong' + TEXT_SEL
PROD_PRICE_BOLETO_OFFER = '.preco_desconto_avista-cm' + TEXT_SEL
PROD_BOLETO_DISCOUNT = '.preco_desconto font' + TEXT_SEL
PROD_BOLETO_DISCOUNT_OFFER = '.preco_normal-cm' + TEXT_SEL
PARCEL_TABLE = '.ParcelamentoCartao ul *' + TEXT_SEL
PARCEL_TABLE_OFFER = '.ParcelamentoCartao-cm ul *' + TEXT_SEL
# offer
OFFER_SOLD = '.q3' + TEXT_SEL
OFFER_AMOUNT = '.q2' + TEXT_SEL
OFFER_DISCOUNT = '.q1' + TEXT_SEL
OFFER_OLD_PRICE = '.preco_antigo-cm' + TEXT_SEL


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
        meta = {'cat': response.meta['cat']}
        for product in response.css(PRODUCT_DETAILS):
            meta['id'] = product.attrib['data-id']
            meta['prod_url'] = product.attrib['href']
            yield scrapy.Request(product.attrib['href'], self.parse_product, meta=meta)

        for url in response.css(NEXT_PAGE):
            yield scrapy.Request(response.urljoin(url.attrib['href']), self.parse_product_list, meta=meta)

    def parse_product(self, response):
        pl = ProductLoader(response=response)
        pl.add_value('id', response.meta['id'])
        pl.add_css('name', PROD_NAME)
        pl.add_css('brand', PROD_BRAND)
        pl.add_value('category', response.meta['cat'])

        pl.add_css('stars', PROD_STARS)
        pl.add_css('ratings', PROD_REVIEWS)
        pl.add_css('comment_table', PROD_COMMENTS)

        if response.url != response.meta['prod_url']:
            yield self.get_offer(response)
        else:
            self.add_prices(pl)

        pl.add_css('description', PROD_DESC)
        pl.add_css('tech_spec', PROD_SPEC_TABLE + ' p *' + TEXT_SEL)
        pl.add_css('warranty', PROD_SPEC_TABLE + TEXT_SEL)

        yield pl.load_item()

    def get_offer(self, response):
        ol = OfferLoader(response=response)
        ol.add_value('product_id', response.meta['id'])
        ol.add_value('end_date', filter(lambda x: x if 'until' in x else None, response.css('script').getall()))
        ol.add_css('discount', OFFER_DISCOUNT)
        ol.add_css('amount', OFFER_AMOUNT)
        ol.add_css('sold', OFFER_SOLD)
        self.add_prices(ol)
        return ol.load_item()

    def add_prices(self, loader):
        pcs = PricesLoader(selector=loader.selector)
        pcs.add_css('price', PROD_PRICE)
        pcs.add_css('price', PROD_PRICE_OFFER)
        pcs.add_css('old_price', OFFER_OLD_PRICE)
        pcs.add_css('price_boleto', PROD_PRICE_BOLETO)
        pcs.add_css('price_boleto', PROD_PRICE_BOLETO_OFFER)
        pcs.add_css('discount_boleto', PROD_BOLETO_DISCOUNT)
        pcs.add_css('discount_boleto', PROD_BOLETO_DISCOUNT_OFFER)
        pcs.add_value('parcel_table', loader.selector.css(PARCEL_TABLE).getall())
        pcs.add_value('parcel_table', loader.selector.css(PARCEL_TABLE_OFFER).getall())
        loader.add_value('prices', pcs.load_item())
