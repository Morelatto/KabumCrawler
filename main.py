from scrapy import cmdline

cats = ['Memória RAM']
cmd = 'scrapy crawl crawl4r -a cats='.split()
cmd[-1] += ','.join(cats)
cmdline.execute(cmd)
