import json
import urllib.parse

import scrapy

from kabum.items import ProductLoader, PricesLoader, OfferLoader, Offer, Prices

KABUM = 'kabum.com.br'
PAGE_SIZE = 100

JS_DATA_PATTERN = r'\bconst\s+listagemDados\s*=\s*(\[.*?\])\s*\n'


class KabumSpider(scrapy.Spider):
    name = 'kabum'
    allowed_domains = [KABUM]
    parameters = {
        'pagina': 1,
        'ordem': 5,
        'limite': PAGE_SIZE
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')]

    def start_requests(self):
        for url in self.start_urls:
            _url = f'{url}?{urllib.parse.urlencode(self.parameters)}'
            yield scrapy.Request(_url, meta={'url': url, 'parameters': self.parameters.copy()})

    def parse(self, response, **kwargs):
        js_data = response.css('script::text').re_first(JS_DATA_PATTERN)
        json_data = json.loads(js_data)
        if json_data:
            for product in json_data:
                loader = ProductLoader()
                loader.add_value('id', product['codigo'])
                loader.add_value('name', product['nome'])
                loader.add_value('brand', product['fabricante']['nome'])
                loader.add_value('category', product['menu'])
                loader.add_value('offer', self.get_offer(product['oferta']))
                loader.add_value('prices', self.get_prices(product))
                loader.add_value('stars', product['avaliacao_nota'])
                loader.add_value('ratings', product['avaliacao_numero'])
                loader.add_value('image', product['img'])
                loader.add_value('used', product['marketplace'])
                loader.add_value('openbox', product['is_openbox'])
                loader.add_value('available', product['disponibilidade'])
                loader.add_value('url', product['link_descricao'])
                yield loader.load_item()

            response.meta['parameters']['pagina'] += 1
            next_page = f"{response.meta['url']}?{urllib.parse.urlencode(response.meta['parameters'])}"
            yield scrapy.Request(next_page, meta=response.meta)

    @classmethod
    def get_offer(cls, offer) -> Offer:
        if offer:
            loader = OfferLoader()
            loader.add_value('discount', offer['oferta_desconto'])
            loader.add_value('amount', offer['quantidade'])
            loader.add_value('start_date', offer['data_inicio'])
            loader.add_value('end_date', offer['data_fim'])
            loader.add_value('event', offer['evento'])
            return loader.load_item()

    @classmethod
    def get_prices(cls, product) -> Prices:
        loader = PricesLoader()
        loader.add_value('price', product['preco'])
        loader.add_value('price_discount', product['preco_desconto'])
        loader.add_value('price_prime', product['preco_prime'])
        loader.add_value('price_discount_prime', product['preco_desconto_prime'])
        loader.add_value('discount', product['porcentagem_desconto'])
        loader.add_value('discount_prime', product['porcentagem_desconto_prime'])
        loader.add_value('old_price', product['preco_antigo'])
        return loader.load_item()
