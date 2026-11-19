"""
Единый пайплайн подготовки товаров: unloading.csv -> products_ready.csv.

Заменяет цепочку filter_products.py -> compare_products.py -> replace_categories.py
(+ barcode_count.py / brand_count.py как диагностику — теперь это отчёт).

Шаги:
    1. Чтение unloading.csv. Строки с лишними/недостающими колонками не теряются
       молча, а попадают в rejected.csv с причиной.
    2. Нормализация штрихкода; строки без штрихкода отбрасываются.
    3. (необязательно) Оставляем только товары, штрихкоды которых есть в marja.xls.
       Штрихкоды из xls, которых нет в выгрузке, пишутся в marja_not_found.csv.
    4. Удаление дублей по external_id и по штрихкоду (остаётся первая строка).
    5. Замена текстовой категории на UUID по category_mapping.json.
       Ключи сравниваются без учёта пробелов/регистра. Строки с неизвестной
       категорией по умолчанию отбрасываются (как раньше); флаг --keep-unmapped
       оставляет их с пустым category_id.
    6. Нормализация is_active / is_hit к формату "Y" / пусто.
    7. Запись products_ready.csv — ровно в формате, который ждёт
       scripts/import_products.py:
       id, external_id, barcode, article, name, description,
       brand_external_id, is_active, is_hit, image_url, category_id

Запуск (из любой папки):
    python preprocess_products.py unloading.csv
    python preprocess_products.py unloading.csv --marja marja.xls --out-dir out

Все отбракованные строки и сводка лежат в --out-dir (по умолчанию ./out).
Читать .xls нужен пакет xlrd, .xlsx — openpyxl:  pip install pandas xlrd openpyxl
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

OUTPUT_COLUMNS = [
    "id",
    "external_id",
    "barcode",
    "article",
    "name",
    "description",
    "brand_external_id",
    "is_active",
    "is_hit",
    "image_url",
    "category_id",
]

REQUIRED_COLUMNS = ["external_id", "barcode", "name"]
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
TRUE_VALUES = {"y", "yes", "true", "1", "да"}

csv.field_size_limit(sys.maxsize)


# ----------------------------------------------------------------------
# Нормализация
# ----------------------------------------------------------------------

def norm_spaces(value: str) -> str:
    """Схлопывает любые пробелы (в т.ч. неразрывные) в один."""
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def norm_key(value: str) -> str:
    return norm_spaces(value).casefold()


def norm_barcode(value) -> str:
    """'4690327080913', '4690327080913.0', '4,69E+12' -> строка из цифр."""
    text = norm_spaces(str(value)) if value is not None else ""
    if text.lower() in ("", "nan", "none"):
        return ""
    text = text.replace(" ", "")
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".")[0]
    if re.search(r"[eE]", text):
        try:
            return str(int(Decimal(text.replace(",", "."))))
        except (InvalidOperation, ValueError):
            return text
    return text


def norm_flag(value) -> str:
    return "Y" if norm_spaces(value or "").casefold() in TRUE_VALUES else ""


# ----------------------------------------------------------------------
# Чтение
# ----------------------------------------------------------------------

def detect_delimiter(path: Path) -> str:
    with open(path, encoding="utf-8-sig", newline="") as f:
        header = f.readline()
    return max([",", ";", "\t"], key=header.count)


def load_mapping(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    mapping: dict[str, str] = {}
    for key, value in raw.items():
        if not UUID_RE.match(value):
            sys.exit(f"[ошибка] В {path.name} у «{key}» значение не UUID: {value!r}")
        mapping[norm_key(key)] = value
    return mapping


def load_marja_barcodes(path: Path) -> set[str]:
    try:
        import pandas as pd
    except ImportError:
        sys.exit("[ошибка] Для --marja нужен pandas: pip install pandas xlrd openpyxl")
    try:
        df = pd.read_excel(path, dtype=str)
    except ImportError as exc:
        sys.exit(f"[ошибка] Не хватает пакета для чтения Excel: {exc}")
    if "Штрихкод" not in df.columns:
        sys.exit(f"[ошибка] В {path.name} нет колонки 'Штрихкод'. Есть: {list(df.columns)}")
    return {b for b in (norm_barcode(v) for v in df["Штрихкод"]) if b}


# ----------------------------------------------------------------------
# Пайплайн
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="unloading.csv — выгрузка товаров")
    parser.add_argument("--marja", type=Path, help="marja.xls(x) — оставить только товары с этими штрихкодами")
    parser.add_argument(
        "--mapping", type=Path, default=Path(__file__).with_name("category_mapping.json"),
        help="JSON {исходная категория: UUID} (по умолчанию рядом со скриптом)",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument("--delimiter", help="разделитель CSV (по умолчанию определяется сам)")
    parser.add_argument(
        "--keep-unmapped", action="store_true",
        help="не отбрасывать товары с неизвестной категорией (category_id будет пустым)",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    mapping = load_mapping(args.mapping)
    marja = load_marja_barcodes(args.marja) if args.marja else None
    delimiter = args.delimiter or detect_delimiter(args.input)

    rejected: list[dict] = []
    stats = Counter()
    unmapped = Counter()
    category_usage = Counter()

    def reject(line: int, row_id: str, name: str, reason: str) -> None:
        rejected.append({"line": line, "external_id": row_id, "name": name, "reason": reason})
        stats[reason] += 1

    with open(args.input, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        columns = reader.fieldnames or []
        if not columns:
            sys.exit("[ошибка] В CSV нет заголовка")

        category_col = "category" if "category" in columns else ("category_id" if "category_id" in columns else None)
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]
        if missing or category_col is None:
            need = missing + ([] if category_col else ["category"])
            sys.exit(f"[ошибка] В {args.input.name} нет колонок: {need}.\nЕсть: {columns}")

        ready: list[dict] = []
        seen_external: set[str] = set()
        seen_barcode: set[str] = set()
        marja_seen: set[str] = set()

        for row in reader:
            line = reader.line_num
            stats["всего строк"] += 1
            ext = norm_spaces(row.get("external_id") or "")
            name = norm_spaces(row.get("name") or "")

            # 1. Битые строки CSV
            if None in row:
                reject(line, ext, name, "лишние колонки (скорее всего неэкранированная запятая)")
                continue
            if any(v is None for v in row.values()):
                reject(line, ext, name, "недостаточно колонок")
                continue
            if not ext or not name:
                reject(line, ext, name, "нет external_id или названия")
                continue

            # 2. Штрихкод
            barcode = norm_barcode(row.get("barcode"))
            if not barcode:
                reject(line, ext, name, "нет штрихкода")
                continue

            # 3. Фильтр по marja
            if marja is not None:
                if barcode not in marja:
                    reject(line, ext, name, "штрихкода нет в marja")
                    continue
                marja_seen.add(barcode)

            # 4. Дубли
            if ext in seen_external:
                reject(line, ext, name, "дубль external_id")
                continue
            if barcode in seen_barcode:
                reject(line, ext, name, "дубль штрихкода")
                continue

            # 5. Категория
            raw_category = norm_spaces(row.get(category_col) or "")
            if UUID_RE.match(raw_category):
                category_id = raw_category.lower()  # уже UUID
            else:
                category_id = mapping.get(norm_key(raw_category), "")
            if not category_id:
                unmapped[raw_category or "(пусто)"] += 1
                if not args.keep_unmapped:
                    reject(line, ext, name, "категории нет в category_mapping.json")
                    continue

            seen_external.add(ext)
            seen_barcode.add(barcode)
            category_usage[category_id or "(без категории)"] += 1
            ready.append({
                "id": norm_spaces(row.get("id") or ""),
                "external_id": ext,
                "barcode": barcode,
                "article": norm_spaces(row.get("article") or ""),
                "name": name,
                "description": (row.get("description") or "").strip(),
                "brand_external_id": norm_spaces(row.get("brand_external_id") or ""),
                "is_active": norm_flag(row.get("is_active")),
                "is_hit": norm_flag(row.get("is_hit")),
                "image_url": norm_spaces(row.get("image_url") or ""),
                "category_id": category_id,
            })

    # --- Запись результатов ---
    def write_csv(name: str, fieldnames: list[str], rows: list[dict]) -> Path:
        path = args.out_dir / name
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    out_path = write_csv("products_ready.csv", OUTPUT_COLUMNS, ready)
    write_csv("rejected.csv", ["line", "external_id", "name", "reason"], rejected)
    if unmapped:
        write_csv(
            "unmapped_categories.csv", ["category", "products"],
            [{"category": c, "products": n} for c, n in unmapped.most_common()],
        )
    if marja is not None:
        write_csv("marja_not_found.csv", ["barcode"], [{"barcode": b} for b in sorted(marja - marja_seen)])

    # --- Сводка ---
    no_image = sum(1 for r in ready if not r["image_url"])
    no_brand = sum(1 for r in ready if not r["brand_external_id"])
    lines = [
        f"Вход:      {args.input}  (разделитель {delimiter!r})",
        f"Строк:     {stats['всего строк']}",
        f"Готово:    {len(ready)}  ->  {out_path}",
        f"Отброшено: {len(rejected)}  ->  {args.out_dir / 'rejected.csv'}",
    ]
    for reason, n in stats.most_common():
        if reason != "всего строк":
            lines.append(f"    - {reason}: {n}")
    if marja is not None:
        lines.append(f"marja:     штрихкодов {len(marja)}, найдено в выгрузке {len(marja_seen)}, "
                     f"не найдено {len(marja - marja_seen)}  ->  marja_not_found.csv")
    lines.append(f"Без картинки: {no_image};  без бренда: {no_brand}")
    if unmapped:
        lines.append("Неизвестные категории (добавьте в category_mapping.json):")
        for cat, n in unmapped.most_common():
            lines.append(f"    - {cat}: {n}")
    summary = "\n".join(lines)
    (args.out_dir / "summary.txt").write_text(summary + "\n", encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
