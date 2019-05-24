# -*- coding: utf-8 -*-
from scrapy_mongodb import MongoDBPipeline

from k4bum.items import Offer


def mongo_name_format(s):
    return '_'.join(s.split()).lower()


# TODO query by brand
# TODO split by item type (offer)
class MongoDBBrandCollectionsPipeline(MongoDBPipeline):
    def __init__(self, **kwargs):
        super(MongoDBBrandCollectionsPipeline, self).__init__(**kwargs)
        self.curr_cat = None

    def process_item(self, item, spider):
        self.curr_cat = 'offer' if isinstance(item, Offer) else mongo_name_format(item['category'])
        super(MongoDBBrandCollectionsPipeline, self).process_item(item, spider)

    def get_collection(self, name):
        return self.curr_cat, self.database[self.curr_cat]

    def export_item(self, item):
        pass
