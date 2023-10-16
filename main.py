from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from autoria.spiders import CarsSpider


def main() -> None:
    process = CrawlerProcess(get_project_settings())

    process.crawl(CarsSpider)

    process.start()


if __name__ == '__main__':
    main()
