# -*- coding: utf-8 -*-
import scrapy

from itemloaders import ItemLoader
from itemloaders.processors import Identity, MapCompose, TakeFirst

SPEC_TABLE_END = '» Políticas do Site'
SPEC_TABLE_START = 'ESPECIFICAÇÕES TÉCNICAS'

RES_DEFAULT_KEY = 'other'

parse_float_or_int = MapCompose(lambda x: process_float_or_int(x))


def process_float_or_int(value):
    try:
        return eval(value)
    except:
        return value


def parse_comments(table, rows=5):
    return [sum(table[i:i + rows]) / max(rows, 1) for i in range(0, len(table), rows)]


def parse_tech_spec(table):
    res = dict()
    key = None
    for row in table[table.index(SPEC_TABLE_START) + 1:table.index(SPEC_TABLE_END)]:
        if not row.startswith('-') and row.endswith(':'):
            key = row[:-1]
            res[key] = res.get(key, list())
        elif row.startswith('-') and key:
            info = row.split('- ')
            # TODO split on :
            if len(info) > 1:
                res[key] += info[1:]
        elif key:
            if len(res[key]):
                res[key][-1] += ' ' + row
            else:
                res[key].append(row)
        elif row:
            get = res.get(RES_DEFAULT_KEY, list())
            get.append(row)
            res[RES_DEFAULT_KEY] = get
    return res


class Prices(scrapy.Item):
    price = scrapy.Field()
    price_discount = scrapy.Field()
    discount_percentage = scrapy.Field()
    old_price = scrapy.Field()


class PricesLoader(ItemLoader):
    default_item_class = Prices
    default_input_processor = parse_float_or_int
    default_output_processor = TakeFirst()


class Offer(scrapy.Item):
    price = scrapy.Field()
    price_discount = scrapy.Field()
    discount_percentage = scrapy.Field()
    quantity = scrapy.Field()
    start_date = scrapy.Field(input_processor=Identity())
    end_date = scrapy.Field(input_processor=Identity())


class OfferLoader(ItemLoader):
    default_item_class = Offer
    default_input_processor = process_float_or_int
    default_output_processor = TakeFirst()


class PaymentInstallment(scrapy.Item):
    terms = scrapy.Field(input_processor=Identity())
    installment = scrapy.Field()
    amount = scrapy.Field()
    total = scrapy.Field()


class PaymentInstallmentLoader(ItemLoader):
    default_item_class = PaymentInstallment
    default_input_processor = parse_float_or_int
    default_output_processor = TakeFirst()


class PaymentMethod(scrapy.Item):
    method = scrapy.Field(output_processor=TakeFirst())
    installments = scrapy.Field()


class Product(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    offer = scrapy.Field(serializer=Offer)
    prices = scrapy.Field(serializer=Prices)
    payments = scrapy.Field(output_processor=Identity())
    stars = scrapy.Field()
    ratings = scrapy.Field()
    images = scrapy.Field(output_processor=Identity())
    used = scrapy.Field()
    openbox = scrapy.Field()
    available = scrapy.Field()
    prime = scrapy.Field()
    free_shipping = scrapy.Field()
    warranty = scrapy.Field()
    url = scrapy.Field()
    # comment_table = scrapy.Field()
    # description = scrapy.Field()
    # tech_spec = scrapy.Field()
    # warranty = scrapy.Field()


class ProductLoader(ItemLoader):
    default_item_class = Product
    default_output_processor = TakeFirst()

    # comment_table_in = MapCompose(lambda cls: int(cls[-1]))  # float?
    # comment_table_out = Compose(parse_comments, lambda x: parse_comments(x, len(x)), TakeFirst())
    # tech_spec_out = Compose(parse_tech_spec)
