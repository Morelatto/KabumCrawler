import scrapy


class MySpider(scrapy.Spider):
    name = 'k4bum'
    allowed_domains = ['kabum.com.br']
    start_urls = ['https://www.kabum.com.br']

    def parse(self, response):
        pass
