# KabumCrawler

Product crawler for [Kabum](https://kabum.com.br/). Filter and store by category to MongoDB.

## Requirements
* [Scrapy](https://github.com/scrapy/scrapy)
* [scrapy-mongodb](https://github.com/sebdah/scrapy-mongodb)
* [requests](https://github.com/kennethreitz/requests)
* [docopt](https://github.com/docopt/docopt)

## Usage
```
  kabum.py <category>...
  kabum.py --list-categories
  kabum.py -h | --help | --version
```

## Arguments
```
  <category>...         Category to download.
```

## Options
```
  --list-categories     List all product categories.
  -h, --help            Show help message.
  --version             Show version.
 ```

## No MongoDB
To run without Mongo comment the following lines on settings.py:
```
ITEM_PIPELINES = {
    'kabum.pipelines.MongoDBBrandCollectionsPipeline': 300,
}

MONGODB_DATABASE = 'kabum'
MONGODB_COLLECTION = 'products'
MONGODB_ADD_TIMESTAMP = True
MONGODB_UNIQUE_KEY = 'id'
```

Optionally, to save results to file add to settings.py:
```
FEED_URI = 'kabum_results.json'
FEED_EXPORT_ENCODING = 'utf-8'
```
