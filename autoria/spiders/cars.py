import asyncio
import re
from typing import Optional

from requests import Session

from scrapy import Request, Spider, http, Selector

from autoria.items import AutoRiaItem


class CarsSpider(Spider):
    name = "autoria"
    allowed_domains = ["auto.ria.com"]

    rq_session: Optional[Session] = None
    is_next_page: bool = True

    def start_requests(self):
        start_url = "https://auto.ria.com/uk/search/?"

        #  ЯКЩО АВТО ПРОДАНЕ, ТО ОКРІМ ПОСИЛАННЯ, НАЗВИ, ЦІНИ І ПРОБІГУ БІЛЬШЕ НІЧОГО НЕ МАЄ
        filters = {
            "indexName": "auto",  # Авто Б/У
            "sort[0].order": "dates.created.desc",  # Спочатку нові оголошення
            "dates.sold.not": "0000-00-00%2000:00:00",  # Приховати продані
            "size": 100,  # Відображати 100 елементів на сторінці
            "page": "{page}",  # Сторінка
        }
        url = start_url + '&'.join([f"{k}={v}" for k, v in filters.items()])

        with Session() as session:
            self.rq_session = session

            page = 0

            while self.is_next_page is True:
                yield Request(
                    url=url.format(page=page),
                    callback=self.parse,
                )

                page += 1

    async def parse(self, response: http.HtmlResponse, **kwargs) -> None:
        items = response.xpath("/html//div[@class='content-bar']")

        if not items:
            self.is_next_page = False

        for item in response.xpath("/html//div[@class='content-bar']"):
            yield Request(
                url=item.xpath("a/@href").get(),
                callback=self.parse_car,
            )

    async def parse_car(self, response: http.HtmlResponse) -> None:
        if response.xpath("/html//div[@id='autoDeletedTopBlock']").get():
            # Оголошення видалено, пропускаємо його
            return

        body = response.xpath('/html//div[@class="ticket-status-0"]')
        auto_id = response.xpath("/html//body").attrib['data-auto-id']
        user_info = await self.get_user_info(auto_id, body)
        car_info = await self.get_car_info(body)

        yield AutoRiaItem(
            url=response.url,
            **user_info,
            **car_info,
        )

    async def get_user_info(self, auto_id: str, body: Selector) -> dict:
        username = body.xpath("//div[@class='seller_info_name bold']/text()").get()
        company_name = body.xpath("//h4[@class='seller_info_name']/a/text()").get()

        if username := (username or company_name):
            username = username.strip()

        script_el = body.css("script[class^='js-user-secure-']")

        phone_number = await asyncio.to_thread(
            self._user_phone,
            auto_id=auto_id,
            hash_=script_el.attrib['data-hash'],
            expires=script_el.attrib['data-expires'],
        )

        return {
            "username": username,
            "phone_number": phone_number,
        }

    def _user_phone(self, auto_id: str, hash_: str, expires) -> int:
        url = f"https://auto.ria.com/users/phones/{auto_id}?hash={hash_}&expires={expires}"

        with self.rq_session.get(url) as response:
            self.logger.info(response.text)
            response.raise_for_status()

            phone: str = response.json()['formattedPhoneNumber']

        return int('+38' + re.sub(r'\D', '', phone))

    async def get_car_info(self, body: Selector) -> dict:
        title = body.xpath("//h1[@class='head']").attrib['title'].strip()
        price_usd = int(
            re.sub(
                r'\D',
                '',
                body.xpath("//div[@class='price_value']/strong/text()").get()
            )
        )
        if odometer := body.xpath("//div[@class='base-information bold']/span/text()").get():
            try:
                odometer = int(odometer.strip()) * 1000
            except ValueError:
                odometer = None

        auto_content = body.xpath("//main[@class='auto-content']")
        image_url, images_count = self._photo_data(auto_content)
        car_number, car_vin = self._car_vin_checked(auto_content)

        return {
            "title": title,
            "price_usd": price_usd,
            "odometer": odometer,
            "image_url": image_url,
            "images_count": images_count,
            "car_number": car_number,
            "car_vin": car_vin,
        }

    @staticmethod
    def _photo_data(auto_content: Selector) -> tuple[str, int]:
        gallery = auto_content.xpath("//div[@class='gallery-order  carousel']")

        if image_url := (gallery.xpath("//div[starts-with(@class, 'photo-620x465')]/picture/source") or None):
            image_url = image_url.attrib['srcset']

        if images_count := gallery.xpath("//div[@class='action_disp_all_block']/a/text()").get():
            images_count = re.sub(r'\D', '', images_count)
        else:
            images_count = len(gallery.xpath("//div[starts-with(@class, 'photo-620x465')]"))

        return image_url, int(images_count)

    @staticmethod
    def _car_vin_checked(auto_content: Selector) -> tuple[Optional[str], Optional[str]]:
        t_check = auto_content.xpath("//div[starts-with(@class, 't-check')]")

        if car_number := t_check.xpath("//span[@class='state-num ua']/text()").get():
            car_number = car_number.strip()

        if car_vin := t_check.xpath("//span[@class='label-vin' or @class='vin-code']/text()").get():
            car_vin = car_vin.strip()

        return car_number, car_vin
