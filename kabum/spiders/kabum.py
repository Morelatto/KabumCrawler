import urllib.parse

import scrapy
from itemloaders import ItemLoader

from kabum.items import Product, Offer, Prices, PaymentMethod, PaymentInstallment
from kabum.items import ProductLoader, OfferLoader, PricesLoader, PaymentInstallmentLoader

PAGE_SIZE = 100

SITE_URL = 'https://www.kabum.com.br'
API_URL = 'https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v1/products-by-category'


class KabumSpider(scrapy.Spider):
    name = 'kabum'
    parameters = {
        'page_number': 1,
        'page_size': PAGE_SIZE,
        'sort': 'most_searched',
        'include': 'gift'
    }

    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories.split(',')

    def start_requests(self):
        for category in self.categories:
            _url = f'{API_URL}/{category}?{urllib.parse.urlencode(self.parameters)}'
            yield scrapy.Request(_url, meta={'parameters': self.parameters.copy(), 'category': category})

    def parse(self, response, **kwargs) -> Product:
        json_response = response.json()
        json_data = json_response['data']
        if json_data:
            for product_data in json_data:
                loader = ProductLoader()
                loader.add_value('id', product_data.get('id'))
                product = product_data['attributes']
                loader.add_value('name', product.get('title'))
                loader.add_value('brand', product.get('manufacturer', {}).get('name'))
                loader.add_value('category', response.meta['category'])
                loader.add_value('offer', self.get_offer(product.get('offer')))
                loader.add_value('prices', self.get_prices(product))
                loader.add_value('payments', self.get_payments(product.get('payment_methods_default')))
                loader.add_value('stars', product.get('score_of_ratings'))
                loader.add_value('ratings', product.get('number_of_ratings'))
                loader.add_value('images', product.get('images'))
                loader.add_value('used', product.get('is_marketplace'))
                loader.add_value('openbox', product.get('is_openbox'))
                loader.add_value('available', product.get('available'))
                loader.add_value('prime', product.get('is_prime'))
                loader.add_value('free_shipping', product.get('has_free_shipping'))
                loader.add_value('warranty', product.get('warranty'))
                loader.add_value('url', f"{SITE_URL}/produto/{product_data.get('id')}")
                yield loader.load_item()

            response.meta['parameters']['page_number'] += 1
            next_page = f"{API_URL}/{response.meta['category']}?{urllib.parse.urlencode(response.meta['parameters'])}"
            yield scrapy.Request(next_page, meta=response.meta)

    @classmethod
    def get_offer(cls, offer) -> Offer:
        if offer:
            loader = OfferLoader()
            loader.add_value('price', offer.get('price'))
            loader.add_value('price_discount', offer.get('price_with_discount'))
            loader.add_value('discount_percentage', offer.get('discount_percentage'))
            loader.add_value('quantity', offer.get('quantity_available'))
            loader.add_value('start_date', offer.get('starts_at'))
            loader.add_value('end_date', offer.get('ends_at'))
            return loader.load_item()

    @classmethod
    def get_prices(cls, product) -> Prices:
        loader = PricesLoader()
        loader.add_value('price', product.get('price'))
        loader.add_value('price_discount', product.get('price_with_discount'))
        loader.add_value('discount_percentage', product.get('discount_percentage'))
        loader.add_value('old_price', product.get('old_price'))
        return loader.load_item()

    def get_payments(self, payments) -> PaymentMethod:
        if payments:
            for payment in payments:
                loader = ItemLoader(item=PaymentMethod())
                loader.add_value('method', payment.get('method'))
                loader.add_value('installments', self.get_installments(payment))
                yield loader.load_item()

    @classmethod
    def get_installments(cls, payment) -> PaymentInstallment:
        for installment in payment.get('installments', []):
            loader = PaymentInstallmentLoader()
            loader.add_value('terms', installment.get('payment_terms'))
            loader.add_value('installment', installment.get('installment'))
            loader.add_value('amount', installment.get('amount'))
            loader.add_value('total', installment.get('total'))
            yield loader.load_item()
