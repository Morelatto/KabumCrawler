# -*- coding: utf-8 -*-
import re

import scrapy

from lxml.html.clean import unicode
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, MapCompose, Identity

IS_CURRENCY_RE = r'([\d+.]*\d+,\d+)'

SPEC_TABLE_END = '» Políticas do Site'
SPEC_TABLE_START = 'ESPECIFICAÇÕES TÉCNICAS'

RES_DEFAULT_KEY = 'other'

clean_tags = MapCompose(unicode.strip)
to_int = MapCompose(lambda i: re.findall(r'\d+', i), int)


def get_currency(s):
    m = re.findall(IS_CURRENCY_RE, s)
    if m:
        return m[0]


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
        else:
            get = res.get(RES_DEFAULT_KEY, list())
            get.append(row)
            res[RES_DEFAULT_KEY] = get
    return res


class Product(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()

    stars = scrapy.Field()
    ratings = scrapy.Field()
    comment_table = scrapy.Field()

    prices = scrapy.Field(input_processor=Identity())

    description = scrapy.Field()
    tech_spec = scrapy.Field()
    warranty = scrapy.Field()


class Offer(scrapy.Item):
    product_id = scrapy.Field()

    end_date = scrapy.Field()
    discount = scrapy.Field()
    amount = scrapy.Field()
    sold = scrapy.Field()

    prices = scrapy.Field()


class Prices(scrapy.Item):
    price = scrapy.Field()
    old_price = scrapy.Field()
    price_boleto = scrapy.Field()
    discount_boleto = scrapy.Field()
    parcel_table = scrapy.Field()


class ProductLoader(ItemLoader):
    default_item_class = Product
    default_input_processor = clean_tags
    default_output_processor = TakeFirst()

    stars_in = to_int
    ratings_in = to_int
    comment_table_in = MapCompose(lambda cls: int(cls[-1]))  # float?
    comment_table_out = Compose(parse_comments, lambda x: parse_comments(x, len(x)), TakeFirst())

    tech_spec_out = Compose(parse_tech_spec)


class OfferLoader(ItemLoader):
    default_item_class = Offer
    default_input_processor = to_int
    default_output_processor = TakeFirst()

    end_date_in = Identity()  # TODO regex parsing js
    discount_in = to_int
    prices_in = Identity()


class PricesLoader(ItemLoader):
    default_item_class = Prices
    default_input_processor = clean_tags
    default_output_processor = Compose(TakeFirst(), get_currency)

    discount_boleto_in = to_int
    discount_boleto_out = TakeFirst()
    parcel_table_out = MapCompose(str.strip, lambda x: x if x else None, lambda v: v.split()[2])
