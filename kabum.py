"""Script to download products from kabum.com.br
Usage:
  kabum.py <category>...
  kabum.py --list-categories
  kabum.py -h | --help | --version

Arguments:
  <category>...         Category to download. E.g.: hardware, tv

Options:
  --list-categories     List all product categories.
  -h, --help            Show this help message.
  --version             Show version.
"""
import requests
from docopt import docopt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kabum.spiders.kabum import KabumSpider

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.86 Safari/537.36 '
}

CATEGORIES_URL = 'https://servicespub.prod.api.aws.grupokabum.com.br/categoria/v1/categoria'
ACTIVE_PARAM = '?ativo=1'


def fetch_categories():
    categories = {}
    r = requests.get(CATEGORIES_URL + ACTIVE_PARAM, headers=headers)
    if r.status_code == 200:
        res = r.json()
        for cat in res['categorias']:
            categories[cat['nome']] = cat['amigavel']
    else:
        print(f'Got {r.status_code} response code fetching categories')
    return categories


def get_category(categories):
    print("=" * 9)
    print("CATEGORY")
    print("=" * 9)
    for i, cat in enumerate(categories):
        print(i + 1, cat)
    while True:
        try:
            n = input('> Enter category number: ')
            cat_list = list(categories)
            n = int(n)
            if 0 < n <= len(cat_list):
                category = categories[cat_list[n - 1]]
                return category
            else:
                raise Exception
        except KeyboardInterrupt:
            return
        except:
            print('Invalid category number')


def fetch_subcategories(sub_category):
    sub_categories = {}
    r = requests.get(f'{CATEGORIES_URL}/{sub_category}' + ACTIVE_PARAM, headers=headers)
    if r.status_code == 200:
        res = r.json()
        for sub_cat in res['categorias']:
            sub_categories[sub_cat['nome']] = sub_cat['amigavel']
    else:
        print(f'Got {r.status_code} response code fetching sub categories')
    return sub_categories


def get_sub_category(sub_categories):
    print("=" * 12)
    print("SUB CATEGORY")
    print("=" * 12)
    for i, sub_category in enumerate(sub_categories):
        print(i + 1, sub_category)
    while True:
        try:
            n = input('> Enter subcategory number: ')
            sub_cat_list = list(sub_categories)
            n = int(n)
            if 0 < n <= len(sub_cat_list):
                return sub_categories[sub_cat_list[n - 1]]
            else:
                raise Exception
        except KeyboardInterrupt:
            return
        except:
            print('Invalid subcategory number')


def execute(urls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(KabumSpider, categories=urls)
    process.start()
    process.stop()


def main():
    if args['<category>']:
        execute(args['<category>'])
    elif args['--list-categories']:
        categories = fetch_categories()
        if categories:
            category = get_category(categories)
            sub_categories = fetch_subcategories(category)
            if sub_categories:
                sub_category = get_sub_category(sub_categories)
                execute(f'{category}/{sub_category}')


if __name__ == '__main__':
    args = docopt(__doc__, version='0.3')
    main()
