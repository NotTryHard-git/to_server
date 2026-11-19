import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.database import async_session_maker
from app.modules.catalog.models import Category
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession




# Структура:
# {
#     "Название категории": [
#         "Дочерняя категория",
#         ...
#     ]
# }
#
# Если у категории нет детей, можно указать [].

CATEGORIES = {
    "Декоративная косметика": {
        "Косметика для лица": [
            "Бронзеры для лица",
            "Консилеры для лица",
            "Праймеры и основы под макияж",
            "Пудры для лица",
            "Румяна для лица",
            "Скульпторы и контуринг для лица",
            "Спреи для фиксации макияжа",
            "Тинты для лица",
            "Тональные основы для лица",
            "Хайлайтеры для лица",
        ],
        "Косметика для глаз": [
            "Глиттеры для глаз",
            "Карандаши для глаз",
            "Подводки для глаз",
            "Тени для век",
            "Туши для ресниц",
        ],
        "Косметика для бровей": [
            "Гели для бровей",
            "Карандаши для бровей",
            "Маркеры и лайнеры для бровей",
            "Мыло для бровей",
            "Сыворотки для бровей",
            "Тинты для бровей",
            "Туши для бровей",
        ],
        "Косметика для губ": [
            "Бальзамы для губ",
            "Блески для губ",
            "Карандаши для губ",
            "Масла для губ",
            "Помады для губ",
            "Пламперы для губ",
            "Тинты для губ",
        ],
    },

    "Уход за кожей": {
        "Средства для ухода за лицом": [
            "Гели и пенки для умывания",
            "Кремы для лица",
            "Лосьоны для лица",
            "Маски для лица",
            "Мицеллярная вода и демакияж",
            "Патчи для глаз",
            "Пилинги и скрабы для лица",
            "Очищающие пэды для лица",
            "Сыворотки для лица",
            "Тоники для лица",
            "Энзимные пудры",
        ],
        "Средства для ухода за телом": [
            "Баттеры для тела",
            "Гели для душа и очищения",
            "Кремы для тела",
            "Лосьоны для тела",
            "Мисты для тела",
            "Скрабы для тела",
        ],
        "Средства для депиляции": [
            "Крем для депиляции",
            "Крем-парафин",
            "Пасты для шугаринга и депиляции",
        ],
        "Средства для и после загара": [
            "Автозагары для лица и тела",
            "Кремы и эмульсии после загара (помогает разделить SOS-средства)",
            "Масла для загара",
            "Солнцезащитные кремы и эмульсии (SPF)",
            "Солнцезащитные спреи",
            "Солнцезащитные стики",
        ],
    },

    "Уход за волосами": {
        "Очищение и базовый уход": [
            "Бальзамы для волос",
            "Кондиционеры для волос",
            "Маски для волос",
            "Шампуни для волос",
        ],
        "Специальный и несмываемый уход": [
            "Дымки и мисты для волос",
            "Масла для волос",
            "Сыворотки и флюиды для волос",
        ],
        "Стайлинг и укладка": [
            "Гели для укладки волос",
            "Лаки для волос",
            "Муссы и пенки для волос",
            "Пасты и глина для стилизации",
            "Спреи для фиксации и термозащиты",
            "Спреи-воски для волос",
        ],
        "Окрашивание волос": [
            "Краски для волос",
            "Оттеночные бальзамы и тоники",
        ],
    },

    "Маникюр и педикюр": {
        "Базы, топы и покрытия": [
            "Базовые покрытия для ногтей (базы)",
            "Гель-лаки для ногтей",
            "Лаки для ногтей (классические)",
            "Топовые покрытия для ногтей (топы)",
        ],
        "Уход за ногтями и кутикулой": [
            "Масла для кутикулы",
            "Средства для укрепления ногтей",
        ],
        "Инструменты для маникюра и педикюра": [
            "Кусачки и ножницы для ногтей/кутикулы",
            "Пилки и бафы для ногтей",
            "Пушеры и апельсиновые палочки",
        ],
        "Жидкости и средства для снятия": [
            "Жидкости для снятия лака и гель-лака",
            "Средства для обезжиривания ногтей",
        ],
    },

    "Парфюмерия": {
        "Женская": [],
        "Мужская": [],
        "Нишевая парфюмерия": [],
    },
}


async def create_category(
    db: AsyncSession,
    name: str,
    parent_id=None,
    sort_order: int = 0,
) -> Category:
    category = Category(
        name=name,
        parent_id=parent_id,
        sort_order=sort_order,
    )

    db.add(category)

    # Нам нужен id, чтобы использовать его
    # как parent_id для дочерних категорий.
    await db.flush()

    return category


async def seed_categories():
    async with async_session_maker() as db:
        try:
            # Чтобы скрипт можно было безопасно запускать повторно.
            existing_result = await db.execute(select(Category))
            existing_categories = existing_result.scalars().all()

            existing_by_name = {
                category.name: category
                for category in existing_categories
            }

            root_sort_order = 0

            for root_name, subcategories in CATEGORIES.items():

                # -------------------------
                # ROOT CATEGORY
                # -------------------------

                root = existing_by_name.get(root_name)

                if root is None:
                    root = await create_category(
                        db=db,
                        name=root_name,
                        parent_id=None,
                        sort_order=root_sort_order,
                    )

                    existing_by_name[root_name] = root

                root_sort_order += 1

                # -------------------------
                # SECOND LEVEL
                # -------------------------

                sub_sort_order = 0

                for subcategory_name, children in subcategories.items():

                    subcategory = existing_by_name.get(subcategory_name)

                    if subcategory is None:
                        subcategory = await create_category(
                            db=db,
                            name=subcategory_name,
                            parent_id=root.id,
                            sort_order=sub_sort_order,
                        )

                        existing_by_name[subcategory_name] = subcategory

                    else:
                        # Если категория уже существует,
                        # восстанавливаем правильную иерархию.
                        subcategory.parent_id = root.id
                        subcategory.sort_order = sub_sort_order

                    sub_sort_order += 1

                    # -------------------------
                    # THIRD LEVEL
                    # -------------------------

                    child_sort_order = 0

                    for child_name in children:

                        child = existing_by_name.get(child_name)

                        if child is None:
                            child = await create_category(
                                db=db,
                                name=child_name,
                                parent_id=subcategory.id,
                                sort_order=child_sort_order,
                            )

                            existing_by_name[child_name] = child

                        else:
                            # Если категория уже существует,
                            # устанавливаем правильного родителя.
                            child.parent_id = subcategory.id
                            child.sort_order = child_sort_order

                        child_sort_order += 1

            await db.commit()

            print("Категории успешно добавлены!")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_categories())