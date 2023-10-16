# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Spider

from autoria.items import AutoRiaItem
from database import get_session, UsedCarRepo
from config import Setting


class AutoriaPipeline:
    def open_spider(self, spider: Spider) -> None:
        orm_session = get_session(Setting.DATABASE_URL)

        self.repository: UsedCarRepo = UsedCarRepo(orm_session)  # NOQA
        self.orm_session = orm_session  # NOQA

    def close_spider(self, spider: Spider) -> None:
        self.orm_session.close()

    def process_item(self, item: AutoRiaItem, spider: Spider) -> AutoRiaItem:
        adapter = ItemAdapter(item)

        if adapter['car_vin'] is None:
            # Не записуємо в бд авто, які не мають VIN-номер.
            # Це здебільше якісь причіпи, катера
            return item

        if not self.repository.exists_by_url(adapter['url']):
            self.repository.create_car(adapter.asdict())

        return item
