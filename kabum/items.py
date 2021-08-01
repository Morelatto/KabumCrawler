# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

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
    price_prime = scrapy.Field()
    price_discount_prime = scrapy.Field()
    discount = scrapy.Field()
    discount_prime = scrapy.Field()
    old_price = scrapy.Field()


class PricesLoader(ItemLoader):
    default_item_class = Prices
    default_input_processor = parse_float_or_int
    default_output_processor = TakeFirst()


class Offer(scrapy.Item):
    discount = scrapy.Field()
    amount = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    event = scrapy.Field()


class OfferLoader(ItemLoader):
    default_item_class = Offer
    default_output_processor = TakeFirst()

    discount_in = process_float_or_int
    amount_in = process_float_or_int


class Product(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    offer = scrapy.Field(serializer=Offer)
    prices = scrapy.Field(serializer=Prices)
    stars = scrapy.Field()
    ratings = scrapy.Field()
    image = scrapy.Field()
    used = scrapy.Field()
    openbox = scrapy.Field()
    available = scrapy.Field()
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
