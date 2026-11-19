# Пайплайн подготовки товаров

`unloading.csv` (выгрузка из Bitrix/1С) → `products_ready.csv` → `scripts/import_products.py`.

```bash
pip install pandas xlrd openpyxl
python scripts/preprocess/preprocess_products.py unloading.csv --marja marja.xls --out-dir out
python scripts/import_products.py out/products_ready.csv
```

В `out/` помимо `products_ready.csv` — `rejected.csv` (строки с причиной отбраковки), `marja_not_found.csv`, сводка и список неизвестных категорий.

`category_mapping.json` — соответствие «текстовая категория из выгрузки → UUID категории в БД». **UUID привязаны к конкретной базе**: на новом сервере `seed_categories.py` создаст другие UUID, поэтому после засева категорий файл нужно перегенерировать (или переносить базу дампом). Файл в репозитории восстановлен из `replace_categories.py` — **сверьте количество записей с вашим оригиналом** (в нём 44 категории).
