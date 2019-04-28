# -*- coding: utf-8 -*-
import scrapy


class Product(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    available = scrapy.Field()

    stars = scrapy.Field()
    ratings = scrapy.Field()
    rating_table = scrapy.Field()

    price = scrapy.Field()
    price_boleto = scrapy.Field()
    discount_boleto = scrapy.Field()
    parcel_table = scrapy.Field()

    description = scrapy.Field()
    tech_spec = scrapy.Field()
    warranty = scrapy.Field()