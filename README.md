# KabumCrawler

Crawler de produtos para o [Kabum](https://kabum.com.br/). Salva os produtos em um banco MongoDB separando por categoria.

## Requisitos

* [Scrapy](https://github.com/scrapy/scrapy)
* [scrapy-mongodb](https://github.com/sebdah/scrapy-mongodb)
* [requests](https://github.com/kennethreitz/requests)
* [docopt](https://github.com/docopt/docopt)

## Script

O projeto contém um script que facilita a busca da url de categorias e subcategorias. O crawler pode ser usado sem esse script, porém ele espera o nome das categorias usado internamente no site como parâmetro inicial de busca.

```
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
 ```

## Rodar sem MongoDB

Para rodar sem salvar os resultados em um banco MongoDB é preciso comentar a seguinte linha no arquivo de configurações kabum/settings.py:

```
ITEM_PIPELINES = {
    'kabum.pipelines.MongoDBBrandCollectionsPipeline': 100,
}
```

Para salvar os resultados em um json, adicionar as linhas:

```
FEED_URI = 'kabum.json'
FEED_EXPORT_ENCODING = 'utf-8'
```

## License

Distributed under the GNU License. See LICENSE for more information.