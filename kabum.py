"""Script to download products from kabum.com.br
Usage:
  kabum.py <category_url>...
  kabum.py --list-categories
  kabum.py -h | --help | --version

Arguments:
  <category_url>...         Category urls to download. E.g.: https://www.kabum.com.br/hardware/placa-de-video-vga

Options:
  --list-categories     List all product categories.
  -h, --help            Show this help message.
  --version             Show version.
"""
import requests

from docopt import docopt
from parsel import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kabum.spiders.kabum import KabumSpider

KABUM = 'https://www.kabum.com.br/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.86 Safari/537.36 '
}


def fetch_categories():
    cats = {}
    r = requests.get(KABUM, headers=headers)
    if r.status_code == 200:
        sel = Selector(text=r.text)
        category = None
        for section in sel.css('#menu_left div'):
            class_name = section.xpath("@class").get()
            if class_name == 'icone_categoria':
                category = section.css('.h2titcategoria::text').get()
            elif class_name == 'texto_categoria':
                sub_category = section.css('p a')
                titles = sub_category.css('::text').getall()
                urls = sub_category.css('::attr(href)').getall()
                cats[category] = dict(zip(titles, urls))
    else:
        print(f'Got {r.status_code} response code from {KABUM}')
    return cats


def execute(urls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(KabumSpider, start_urls=urls)
    process.start()
    process.stop()


def get_category(all_cats):
    for i, cat in enumerate(all_cats):
        print(i + 1, cat)
    while True:
        try:
            n = input('> Enter category number: ')
            cat_list = list(all_cats)
            n = int(n)
            if 0 < n < len(cat_list):
                category = cat_list[n - 1]
                return category
            else:
                raise Exception
        except:
            print('Invalid category number')


def get_sub_category(all_sub_cats):
    for i, sub_category in enumerate(all_sub_cats):
        print(i + 1, sub_category)
    while True:
        try:
            n = input('> Enter subcategory number: ')
            sub_cat_list = list(all_sub_cats)
            n = int(n)
            if 0 < n < len(sub_cat_list):
                return sub_cat_list[n - 1]
            else:
                raise Exception
        except:
            print('Invalid subcategory number')


def main():
    urls = []
    if args['<category_url>']:
        urls = args['<category_url>']
    elif args['--list-categories']:
        all_cats = fetch_categories()
        cat = get_category(all_cats)
        sub_cat = get_sub_category(all_cats[cat])
        urls = [all_cats[cat][sub_cat]]
    execute(urls)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.2')
    main()
