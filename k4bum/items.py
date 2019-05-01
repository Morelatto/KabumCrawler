# -*- coding: utf-8 -*-
import scrapy

from lxml.html.clean import unicode
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, MapCompose


SPEC_TABLE_END = '» Políticas do Site'
SPEC_TABLE_START = 'ESPECIFICAÇÕES TÉCNICAS'

RES_DEFAULT_KEY = 'other'

to_int = MapCompose(int)


class Product(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()

    stars = scrapy.Field()
    ratings = scrapy.Field()
    comment_table = scrapy.Field()

    price = scrapy.Field()
    price_boleto = scrapy.Field()
    discount_boleto = scrapy.Field()
    parcel_table = scrapy.Field()

    description = scrapy.Field()
    tech_spec = scrapy.Field()
    warranty = scrapy.Field()


def get_currency(s):
    return s.split()[-1]


get_currency_proc = Compose(TakeFirst(), get_currency)


def parse_comments(table, rows=5):
    return [sum(table[i:i + rows]) / max(rows, 1) for i in range(0, len(table), rows)]


def parse_tech_spec(table):
    res = {RES_DEFAULT_KEY: []}
    key = None
    for row in table[table.index(SPEC_TABLE_START) + 1:table.index(SPEC_TABLE_END)]:
        if not row.startswith('-') and row.endswith(':'):
            key = row[:-1]
            res[key] = res.get(key, list())
        elif row.startswith('-') and key:
            info = row.split('- ')
            if len(info) > 1:
                res[key] += info[1:]
        elif key:
            if len(res[key]):
                res[key][-1] += ' ' + row
            else:
                res[key].append(row)
        else:
            res[RES_DEFAULT_KEY].append(row)
    return res


class ProductLoader(ItemLoader):
    default_item_class = Product
    default_input_processor = MapCompose(unicode.strip, lambda x: x if x else None)
    default_output_processor = TakeFirst()

    stars_in = to_int
    ratings_in = to_int
    comment_table_in = MapCompose(lambda cls: int(cls[-1]))  # float?
    comment_table_out = Compose(parse_comments, lambda x: parse_comments(x, len(x)), TakeFirst())

    price_out = get_currency_proc
    price_boleto_out = get_currency_proc
    discount_boleto_out = Compose(TakeFirst(), lambda t: t.split('%')[0], int)  # index may fail

    parcel_table_out = MapCompose(lambda v: v.split()[2])

    tech_spec_out = Compose(parse_tech_spec)
