"""Usage:
  cats.py [<category>]
  cats.py -h | --help | --version
"""
import json
import requests

from docopt import docopt
from parsel import Selector
from scrapy import cmdline

KABUM = 'https://www.kabum.com.br/'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}

cmd = ["scrapy", "crawl", "kabum", "-a"]


def get_all_cats():
    all_cats, i = [], 1
    r = requests.get(KABUM, headers=headers)
    if r.status_code == 200:
        sel = Selector(text=r.text)
        for cat in sel.css('.bot-categoria a'):
            name, link = cat.css('::text').get(), cat.attrib['href']
            all_cats.append((name, link[25:]))
            print(i, name)
            i += 1
    return all_cats


def main():
    cats = get_all_cats()
    cmd.append('all_cats=' + json.dumps([c[1] for c in cats]))
    if not args['<category>']:
        # TODO parse 1-5
        n = input('# ')
        if n:
            cat_url = cats[int(n) - 1][1]
    else:
        for name, url in cats:
            if args['<category>'].lower() == name.lower():
                cat_url = url
    cmd.append('-a')
    cmd.append('cat=' + cat_url)
    cmdline.execute(cmd)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main()
