import asyncio

import aiohttp
from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag

from telegram_bot.models import ActualCurrencyInfo

from . import consts


async def fetch_files(
    url: str, session: aiohttp.ClientSession, city: str, fields: list[str], objects: list[ActualCurrencyInfo]
):
    async with session.get(url + city) as response:
        return await parse_files(await response.read(), city, fields, objects)


async def parse_files(
    data: bytes, city: str, fields: list[str], objects: list[ActualCurrencyInfo]
) -> list[ActualCurrencyInfo]:
    soup: BeautifulSoup = BeautifulSoup(data, "lxml")
    table_currency: Tag = soup.find("tbody", {"id": "currency_tbody"})
    banks: ResultSet = table_currency.findAll("tr")
    for bank in banks:
        data: dict[str, str] = {}
        if bank.has_attr("data-bank_id"):
            counter = 0
            for td in bank:
                if not isinstance(td, NavigableString):
                    if td.find("span"):
                        bank_name = td.find("span").get_text()
                        data["city"] = city
                        data["bank"] = bank_name
                        continue
                    data[fields[counter]] = td.get_text() if td.get_text() != "-" else None
                    counter += 1
            objects.append(ActualCurrencyInfo(**data))
    return objects


async def get_currency_rate() -> list[ActualCurrencyInfo]:
    async with aiohttp.ClientSession(headers={"User-agent": "your bot 0.2"}) as session:
        objects: list[ActualCurrencyInfo] = []
        tasks: list[asyncio.Task] = []
        fields: list[str] = [f.name for f in ActualCurrencyInfo._meta.fields][5:]
        for city in consts.CityCallbackChoices.labels:
            tasks.append(asyncio.create_task(fetch_files(consts.SOURCE, session, city, fields, objects)))
        await asyncio.gather(*tasks)
        return objects
