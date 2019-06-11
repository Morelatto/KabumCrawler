"""Script to download products from kabum.com.br
Usage:
  kabum.py <category>...
  kabum.py --list-categories
  kabum.py -h | --help | --version

Arguments:
  <category>...         Category to download.

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
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


def fetch_categories():
    cats = []
    r = requests.get(KABUM, headers=headers)
    if r.status_code == 200:
        i, sel = 1, Selector(text=r.text)
        for cat in sel.css('.bot-categoria a'):
            name, link = cat.css('::text').get(), cat.attrib['href']
            cats.append((name, link[25:]))
            print(i, name)
            i += 1
    return cats


def execute(cat_urls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(KabumSpider, cats=';'.join(cat_urls))
    process.start()
    process.stop()


def main():
    all_cats, urls = fetch_categories(), []
    if args['<category>']:
        for cat in args['<category>']:
            for name, url in all_cats:
                if cat.lower() == name.lower():
                    urls.append(url)

        if not urls or (len(urls) != len(args['<category>'])):
            print('URL not found for some category', urls, args['<category>'])
            return

    elif args['--list-categories']:
        n = input('# ')
        if n:
            for x in set(n.split(',')):
                urls.append(all_cats[int(x) - 1][1])
    execute(urls)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main()
