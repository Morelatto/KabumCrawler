# -*- coding: utf-8 -*-

BOT_NAME = 'kabum'

SPIDER_MODULES = ['kabum.spiders']
NEWSPIDER_MODULE = 'kabum.spiders'

USER_AGENT = \
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_DEBUG = True


TELNETCONSOLE_ENABLED = False
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

ITEM_PIPELINES = {
    'scrapy_mongodb.MongoDBPipeline': 300,
}

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'kabum'
MONGODB_COLLECTION = 'products'
MONGODB_ADD_TIMESTAMP = True
MONGODB_UNIQUE_KEY = 'id'
