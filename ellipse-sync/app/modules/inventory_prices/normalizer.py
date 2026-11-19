"""Приведение «чего угодно от 1С» к каноническому виду для ellipse-back.

Формат реальной выгрузки 1С на момент написания неизвестен, поэтому этот слой
намеренно терпим к вариациям. Если формат окажется другим — правится ТОЛЬКО этот
файл (или список алиасов в FIELD_ALIASES_FILE), остальной код не меняется.

Что понимаем:
  * тело — объект {"items": [...]} (или data / rows / records / products / offers /
    Товары / Остатки ...) либо просто список строк;
  * имена полей — по списку алиасов (латиница и кириллица, любой регистр,
    с пробелами/подчёркиваниями/дефисами);
  * магазин на уровне пачки или группы: {"store_external_id": "...", "items": [...]};
  * числа строкой с пробелами и запятой ("1 234,50"), GUID в любом регистре,
    в фигурных скобках или без дефисов, числа-коды (11111.0), "Да/Нет", "Y".

Строки, которые не получилось разобрать, не роняют пачку: они уходят в `rejected`
с причиной и попадают в журнал синхронизации вместе с исходным телом запроса.
"""
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any

MAX_PRICE = Decimal("99999999.99")
MAX_QUANTITY = 10_000_000
CENT = Decimal("0.01")

DEFAULT_ALIASES: dict[str, list[str]] = {
    "product": [
        "product_external_id", "product_id", "productid", "product", "nomenclature_id",
        "nomenclature", "item_id", "guid", "ref", "uid", "external_id", "id_tovara",
        "Номенклатура", "НоменклатураГУИД", "НоменклатураСсылка", "ИдТовара", "ИД_Товара",
        "ГУИД", "Товар", "КодТовара", "ИдентификаторТовара",
    ],
    "store": [
        "store_external_id", "store_id", "storeid", "store", "warehouse_id", "warehouse",
        "shop_id", "shop", "id_sklada", "Склад", "СкладГУИД", "ИдСклада", "ИД_Склада",
        "ГУИДСклада", "Магазин", "ИдМагазина", "Подразделение", "ИдентификаторСклада",
    ],
    "quantity": [
        "quantity", "qty", "count", "stock", "balance", "amount", "remainder", "rest",
        "Количество", "Остаток", "Остатки", "КолВо", "Кол", "СвободныйОстаток", "ВНаличии",
    ],
    "price": [
        "price", "retail_price", "cost", "Цена", "РозничнаяЦена", "ЦенаРозница", "ЦенаПродажи",
    ],
    "old_price": [
        "old_price", "oldprice", "price_old", "price_before", "crossed_price",
        "СтараяЦена", "ЦенаДоСкидки", "ЦенаБезСкидки", "ПрежняяЦена",
    ],
    "currency": ["currency", "cur", "Валюта", "КодВалюты"],
    # Служебные поля пачки
    "batch_id": ["batch_id", "batchid", "batch", "ИдПакета", "НомерВыгрузки", "ИдВыгрузки"],
    "mode": ["mode", "sync_mode", "Режим", "ТипВыгрузки"],
    "final": ["final", "is_final", "last", "is_last", "Последняя", "ПоследняяПорция"],
    "stores": ["stores", "store_ids", "warehouses", "Магазины", "Склады"],
}

ROW_CONTAINERS = [
    "items", "data", "rows", "records", "products", "offers", "list", "result",
    "Товары", "Остатки", "Данные", "Строки", "Номенклатура", "Предложения",
]

CURRENCY_MAP = {
    "RUB": "RUB", "RUR": "RUB", "РУБ": "RUB", "РУБ.": "RUB", "РУБЛЬ": "RUB",
    "РУБЛЕЙ": "RUB", "643": "RUB", "₽": "RUB",
}

_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_HEX32 = re.compile(r"^[0-9a-fA-F]{32}$")
_NUMBER = re.compile(r"^[+-]?\d+(\.\d+)?$")
_TRUE = {"1", "true", "yes", "y", "да", "истина", "д", "t"}
_FALSE = {"0", "false", "no", "n", "нет", "ложь", "f", ""}


def _key(name: Any) -> str:
    return re.sub(r"[\s_\-.]+", "", str(name)).casefold()


class RowError(ValueError):
    """Строка не может быть принята (причина — в тексте исключения)."""


# ----------------------------------------------------------------------
# Значения
# ----------------------------------------------------------------------

def norm_id(value: Any, label: str) -> str:
    if value is None or isinstance(value, bool):
        raise RowError(f"пустой идентификатор: {label}")
    if isinstance(value, float):
        value = int(value) if value.is_integer() else value
    text = str(value).strip().strip("{}").strip()
    if not text:
        raise RowError(f"пустой идентификатор: {label}")
    if _UUID.match(text):
        return text.lower()
    if _HEX32.match(text):
        h = text.lower()
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
    if len(text) > 100:
        raise RowError(f"идентификатор длиннее 100 символов: {label}")
    return text


def parse_decimal(value: Any, label: str) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            raise RowError(f"не число: {label}={value!r}") from None
    text = re.sub(r"[\s  ]", "", str(value))
    if text.lower() in {"", "-", "null", "none", "nan", "нет", "н/д"}:
        return None
    text = re.sub(r"(?i)(руб\.?|₽|rub|шт\.?)$", "", text)
    if "," in text and "." in text:
        # последний из разделителей — десятичный, остальные — группы тысяч
        dec = "," if text.rfind(",") > text.rfind(".") else "."
        group = "." if dec == "," else ","
        text = text.replace(group, "").replace(dec, ".")
    else:
        text = text.replace(",", ".")
    if not _NUMBER.match(text):
        raise RowError(f"не число: {label}={value!r}")
    return Decimal(text)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().casefold()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise ValueError(f"не булево значение: {value!r}")


# ----------------------------------------------------------------------
# Результат
# ----------------------------------------------------------------------

@dataclass
class NormalizedBatch:
    items: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    warnings: Counter = field(default_factory=Counter)
    batch_id: str | None = None
    mode: str = "delta"
    final: bool = False
    stores: list[str] = field(default_factory=list)
    error: str | None = None  # ошибка уровня всей пачки


class Normalizer:
    def __init__(self, extra_aliases: dict[str, list[str]] | None = None):
        aliases = {k: list(v) for k, v in DEFAULT_ALIASES.items()}
        for name, more in (extra_aliases or {}).items():
            aliases.setdefault(name, []).extend(more)
        self.aliases = aliases
        self._lookup = {
            name: {_key(a) for a in names} for name, names in aliases.items()
        }
        self._containers = {_key(c) for c in ROW_CONTAINERS}

    @classmethod
    def from_file(cls, path: str) -> "Normalizer":
        if not path:
            return cls()
        extra = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(extra)

    # --- поиск полей ---------------------------------------------------

    def _pick(self, mapping: dict[str, Any], name: str) -> tuple[bool, Any]:
        wanted = self._lookup[name]
        for original, value in mapping.items():
            if _key(original) in wanted:
                return True, value
        return False, None

    def _find_rows(self, container: dict) -> tuple[list | None, dict]:
        """Находит список строк в объекте; остальные поля объекта = значения по умолчанию."""
        for original, value in container.items():
            if _key(original) in self._containers and isinstance(value, list):
                rest = {k: v for k, v in container.items() if k != original}
                return value, rest
        return None, container

    # --- публичный метод -----------------------------------------------

    def normalize(self, body: Any, max_items: int) -> NormalizedBatch:
        result = NormalizedBatch()

        if isinstance(body, list):
            rows, defaults = body, {}
        elif isinstance(body, dict):
            rows, defaults = self._find_rows(body)
            if rows is None:
                result.error = (
                    "Не найден список строк. Ожидается {\"items\": [...]} или просто список. "
                    f"Поля верхнего уровня: {list(body)[:20]}"
                )
                return result
        else:
            result.error = "Тело запроса должно быть JSON-объектом или списком"
            return result

        self._read_meta(defaults, result)
        if result.error:
            return result

        default_store = self._pick(defaults, "store")
        default_currency = self._pick(defaults, "currency")

        flat: list[tuple[int, Any, dict]] = []  # (индекс, строка, унаследованные значения)
        inherited_base = {}
        if default_store[0]:
            inherited_base["store"] = default_store[1]
        if default_currency[0]:
            inherited_base["currency"] = default_currency[1]
        self._flatten(rows, inherited_base, flat, [0])

        if len(flat) > max_items:
            result.error = f"В пачке {len(flat)} строк, максимум {max_items}. Разбейте выгрузку."
            return result

        seen: dict[tuple[str, str], int] = {}
        for index, row, inherited in flat:
            try:
                item = self._row(row, inherited, result.warnings)
            except RowError as exc:
                result.rejected.append({"index": index, "reason": str(exc), "row": _short(row)})
                continue
            key = (item["product_external_id"], item["store_external_id"])
            if key in seen:
                result.warnings["duplicates_in_batch"] += 1
                result.items[seen[key]] = item  # последняя строка побеждает
            else:
                seen[key] = len(result.items)
                result.items.append(item)

        if result.mode == "full" and not result.batch_id:
            result.error = "mode=full требует batch_id (общий для всех пачек одной выгрузки)"
        return result

    # --- служебные поля пачки ---------------------------------------------

    def _read_meta(self, meta: dict, result: NormalizedBatch) -> None:
        found, value = self._pick(meta, "batch_id")
        if found and value not in (None, ""):
            result.batch_id = str(value).strip()[:100]

        found, value = self._pick(meta, "mode")
        if found and value not in (None, ""):
            text = str(value).strip().casefold()
            if text in {"full", "полная", "полный", "все", "всё"}:
                result.mode = "full"
            elif text in {"delta", "изменения", "дельта", "частичная", "частичный"}:
                result.mode = "delta"
            else:
                result.error = f"Неизвестный mode={value!r}: допустимы delta и full"
                return

        found, value = self._pick(meta, "final")
        if found and value is not None:
            try:
                result.final = parse_bool(value)
            except ValueError as exc:
                result.error = str(exc)
                return

        found, value = self._pick(meta, "stores")
        if found and isinstance(value, list):
            try:
                result.stores = [norm_id(v, "stores") for v in value]
            except RowError as exc:
                result.error = str(exc)

    # --- строки -------------------------------------------------------------

    def _flatten(self, rows: list, inherited: dict, out: list, counter: list[int]) -> None:
        """Разворачивает вложенные группы: {"store": X, "items": [...]} внутри списка."""
        for row in rows:
            if isinstance(row, dict):
                nested, rest = self._find_rows(row)
                if nested is not None:
                    local = dict(inherited)
                    for name in ("store", "currency"):
                        found, value = self._pick(rest, name)
                        if found:
                            local[name] = value
                    self._flatten(nested, local, out, counter)
                    continue
            out.append((counter[0], row, inherited))
            counter[0] += 1

    def _row(self, row: Any, inherited: dict, warnings: Counter) -> dict:
        if not isinstance(row, dict):
            raise RowError("строка не является объектом")

        values: dict[str, Any] = {}
        for name in ("product", "store", "quantity", "price", "old_price", "currency"):
            found, value = self._pick(row, name)
            if found:
                values[name] = value
            elif name in inherited:
                values[name] = inherited[name]

        if "product" not in values:
            raise RowError(
                "не найдено поле товара (ожидалось одно из: "
                f"{', '.join(self.aliases['product'][:6])}…); поля строки: {list(row)[:15]}"
            )
        if "store" not in values:
            raise RowError(
                "не найдено поле магазина/склада (ожидалось одно из: "
                f"{', '.join(self.aliases['store'][:6])}…); поля строки: {list(row)[:15]}"
            )

        product = norm_id(values["product"], "товар")
        store = norm_id(values["store"], "магазин")

        quantity = None
        raw_qty = parse_decimal(values.get("quantity"), "quantity")
        if raw_qty is not None:
            if raw_qty < 0:
                warnings["negative_quantity_to_zero"] += 1
                raw_qty = Decimal(0)
            if raw_qty != raw_qty.to_integral_value():
                warnings["fractional_quantity_floored"] += 1
                raw_qty = raw_qty.to_integral_value(rounding=ROUND_FLOOR)
            if raw_qty > MAX_QUANTITY:
                raise RowError(f"слишком большой остаток: {raw_qty}")
            quantity = int(raw_qty)

        price = parse_decimal(values.get("price"), "price")
        if price is not None:
            if price <= 0:
                warnings["zero_price_ignored"] += 1
                price = None
            else:
                price = price.quantize(CENT, rounding=ROUND_HALF_UP)
                if price > MAX_PRICE:
                    raise RowError(f"слишком большая цена: {price}")

        old_price = parse_decimal(values.get("old_price"), "old_price")
        if old_price is not None:
            old_price = old_price.quantize(CENT, rounding=ROUND_HALF_UP)
            if price is None or old_price <= price or old_price > MAX_PRICE:
                warnings["old_price_dropped"] += 1
                old_price = None

        if quantity is None and price is None:
            raise RowError("нет ни остатка, ни цены")

        currency = "RUB"
        if values.get("currency") not in (None, ""):
            currency = CURRENCY_MAP.get(str(values["currency"]).strip().upper(), "")
            if not currency:
                raise RowError(f"неизвестная валюта: {values['currency']!r}")

        return {
            "product_external_id": product,
            "store_external_id": store,
            "quantity": quantity,
            "price": None if price is None else str(price),
            "old_price": None if old_price is None else str(old_price),
            "currency": currency,
        }


def _short(row: Any, limit: int = 500) -> Any:
    try:
        text = json.dumps(row, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return repr(row)[:limit]
    return row if len(text) <= limit else text[:limit] + "…"
