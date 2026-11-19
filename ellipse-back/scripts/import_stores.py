"""

    external_id
    city      
    address
    phone
    working_hour
    latitude
    longitude



"""
mock = [
  {
    'id': 1,
    'city': 'Томск',
    'adress': 'ТЦ «Акварель», Иркутский тракт, 112',
    'location': [56.511164432293,85.03631754051],
    'phone': '+7 923 409 55 75',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 2,
    'city': 'Томск',
    'adress': 'ТЦ "Любава" проспект Кирова , 37',
    'location': [56.466002,84.969163],
    'phone': '+7 (3822) 56-22-10',
    'working_hours' : 'Пн-Сб 10:00–19:00; Вс 11:00-18:00',
    'photos': [],
  },
  {
    'id': 3,
    'city': 'Томск',
    'adress': 'Ленина проспект, 165',
    'location': [56.498753,84.948808],
    'phone': '+7 (3822) 97-71-43',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 4,
    'city': 'Томск',
    'adress': 'Красноармейская, 149',
    'location': [56.452624597671,84.976338913526],
    'phone': '+7 (3822) 97-70-58',
    'working_hours' : 'Ежедневно 9:00–21:00',
    'photos': [],
  },
  {
    'id': 5,
    'city': 'Томск',
    'adress': 'ТД «Центральный», Красноармейская, 44',
    'location': [56.475507192969,84.966562285215],
    'phone': '+7 (3822) 97-99-83',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 6,
    'city': 'Томск',
    'adress': 'ТЦ «Южный», Нахимова, 38',
    'location': [56.455456186679,84.970806548445],
    'phone': '+7 (3822) 97-71-48',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 7,
    'city': 'Томск',
    'adress': 'ТЦ «Зеркальный риф», Фрунзе проспект, 92г',
    'location': [56.476508693215,84.971861811674],
    'phone': '+7 (3822) 97-71-49',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 8,
    'city': 'Томск',
    'adress': 'Иркутский тракт, 54 ТЦ "БУМ"',
    'location': [56.504442, 85.011923],
    'phone': '+7 (3822) 97-99-54',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 9,
    'city': 'Томск',
    'adress': 'ТРК «Мегаполис», Ленина проспект, 217 ст2',
    'location': [56.513978568209,84.942505641035],
    'phone': '+7 (3822) 97-90-11',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 10,
    'city': 'Томск',
    'adress': 'ТЦ «Искра», проспект Ленина, 97А',
    'location': [56.455456186679,84.970806548445],
    'phone': '+7 (3822) 47-95-66',
    'working_hours' : 'Пн-Пт 10:00–20:00; Сб 10:00–19:00; Вс 11:00–19:00',
    'photos': [],
  },
  {
    'id': 11,
    'city': 'Томск',
    'adress': 'улица Архитекторов, 2',
    'location': [56.493988,85.056417],
    'phone': '+7 (3822) 97-89-00',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 12,
    'city': 'Томск',
    'adress': 'ТЦ «Виктория», Интернационалистов, 17',
    'location': [56.515496548716,84.984886861936],
    'phone': '+7 923 412 94 11',
    'working_hours' : 'Ежедневно 9:00–20:00',
    'photos': [],
  },
  {
    'id': 13,
    'city': 'Томск',
    'adress': 'ТЦ «999», Ленина проспект, 15',
    'location': [56.458152829764,84.951510797536],
    'phone': '+7 (3822) 41-76-39',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 14,
    'city': 'Томск',
    'adress': 'ТЦ «СмайлCity», Учебная, 48д / Котовского, 19/3',
    'location': [56.459313222048,84.965024768019],
    'phone': '+7 (3822) 90-28-83',
    'working_hours' : 'Ежедневно 10:00–21:30',
    'photos': [],
  },
  {
    'id': 15,
    'city': 'Томск',
    'adress': 'Фрунзе проспект, 152',
    'location': [56.476458, 84.991289],
    'phone': '+7 (3822) 97-71-58',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 16,
    'city': 'Томск',
    'adress': 'Иркутский тракт, 194',
    'location': [56.520561573259,85.070225903045],
    'phone': '+7 (3822) 97-64-05',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 17,
    'city': 'Томск',
    'adress': 'проспект Комсомольский, 37',
    'location': [56.4817,84.9811],
    'phone': '+7 (3822) 97-64-90',
    'working_hours' : 'Ежедневно 10:00–20:00',
    'photos': [],
  },
  {
    'id': 18,
    'city': 'Томск',
    'adress': 'ТРЦ Лето (​Нахимова, 8 ст13 )',
    'location': [56.456630457185,84.96043208511],
    'phone': '+7 (3822) 97-64-99',
    'working_hours' : 'Ежедневно 10:00–22:00',
    'photos': [],
  },
  {
    'id': 19,
    'city': 'Кемерово',
    'adress': 'ТЦ "Я", проспект Кузнецкий, 33Б',
    'location': [55.35890715,86.06725253],
    'phone': '8-923-409-77-27',
    'working_hours' : 'Ежедневно 10:00–21:00',
    'photos': [],
  },
  {
    'id': 20,
    'city': 'Новокузнецк',
    'adress': 'ТЦ "Сити Молл" ул. Кирова, 55',
    'location': [53.758894,87.138164],
    'phone': '+7-923-444-30-83',
    'working_hours' : 'Ежедневно 10:00–22:00',
    'photos': [],
  },
  {
    'id': 21,
    'city': 'Новокузнецк',
    'adress': 'ТЦ "Парус" Архитекторов 14а',
    'location': [53.892697, 87.114331],
    'phone': '+7-923-444-30-83',
    'working_hours' : 'Ежедневно 10:00–22:00',
    'photos': [],
  },
  {
    'id': 22,
    'city': 'Северск',
    'adress': 'ТР "Мармелайт" ул. Курчатова 11а',
    'location': [56.593914,84.909578],
    'phone': '+7 (3822) 97-64-70',
    'working_hours' : 'Ежедневно 10:00–21:00',
    'photos': [],
  }
]

import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.modules.stores.models import Store


async def import_stores() -> None:
    """Идемпотентно: магазин ищется по (город, адрес) — при повторном запуске
    обновляется, а не дублируется. external_id (GUID склада из 1С) здесь не трогаем —
    он заполняется отдельно скриптом map_store_external_ids.py."""
    created = 0
    updated = 0

    async with async_session_maker() as db:
        for store in mock:
            city = store["city"].strip()
            address = store["adress"].strip()
            fields = dict(
                phone=store["phone"].strip(),
                working_hours=store["working_hours"].strip(),
                latitude=store["location"][0],
                longitude=store["location"][1],
            )
            existing = (
                await db.execute(
                    select(Store).where(Store.city == city, Store.address == address)
                )
            ).scalars().first()
            if existing:
                for name, value in fields.items():
                    setattr(existing, name, value)
                updated += 1
            else:
                db.add(Store(city=city, address=address, **fields))
                created += 1
        await db.commit()

    print(f"Готово: создано {created}, обновлено {updated}")


if __name__ == "__main__":
    asyncio.run(import_stores())
