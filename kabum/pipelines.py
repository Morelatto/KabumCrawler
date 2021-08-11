# -*- coding: utf-8 -*-
from scrapy_mongodb import MongoDBPipeline


def mongo_name_format(s, sep='_'):
    return s.replace(' ', sep).replace('/', sep).lower()


class MongoDBBrandCollectionsPipeline(MongoDBPipeline):
    def __init__(self, **kwargs):
        super(MongoDBBrandCollectionsPipeline, self).__init__(**kwargs)
        self.category = None

    def process_item(self, item, spider):
        self.category = mongo_name_format(item['category'])
        super(MongoDBBrandCollectionsPipeline, self).process_item(item, spider)

    def get_collection(self, name):
        return self.category, self.database[self.category]

    def export_item(self, item):
        pass
