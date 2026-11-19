import pytest

from app.modules.inventory_prices.normalizer import Normalizer, RowError, norm_id, parse_decimal

N = Normalizer()
GUID = "1c77e97a-062e-11ec-810d-ac1f6b706719"


def run(body, max_items=100):
    return N.normalize(body, max_items)


def test_canonical_format():
    r = run({"items": [{"product_external_id": GUID, "store_external_id": "s1", "quantity": 5,
                        "price": 1290.5, "old_price": 1490, "currency": "RUB"}]})
    assert r.error is None and not r.rejected
    assert r.items == [{"product_external_id": GUID, "store_external_id": "s1", "quantity": 5,
                        "price": "1290.50", "old_price": "1490.00", "currency": "RUB"}]


def test_plain_list_and_cyrillic_fields():
    r = run([{"Номенклатура": GUID.upper(), "Склад": "{ABCDEF01-0000-0000-0000-000000000001}",
              "Остаток": "1 234,0", "Цена": "1 290,50 руб"}])
    assert not r.rejected
    item = r.items[0]
    assert item["product_external_id"] == GUID
    assert item["store_external_id"] == "abcdef01-0000-0000-0000-000000000001"
    assert item["quantity"] == 1234 and item["price"] == "1290.50"


def test_field_name_variants_ignore_case_and_separators():
    r = run({"Data": [{"Product-ID": "p1", "STORE ID": "s1", "Qty": 3}]})
    assert r.items[0]["product_external_id"] == "p1" and r.items[0]["quantity"] == 3


def test_store_on_batch_level_and_grouped_rows():
    r = run({"store_external_id": "s1", "items": [{"product_id": "p1", "qty": 1}, {"product_id": "p2", "qty": 2}]})
    assert [i["store_external_id"] for i in r.items] == ["s1", "s1"]

    r = run({"items": [
        {"store_id": "s1", "items": [{"product_id": "p1", "qty": 1}]},
        {"store_id": "s2", "items": [{"product_id": "p1", "qty": 7}]},
    ]})
    assert [(i["store_external_id"], i["quantity"]) for i in r.items] == [("s1", 1), ("s2", 7)]


def test_numeric_quirks():
    assert parse_decimal("1.234,56", "x") == parse_decimal("1,234.56", "x")
    assert str(parse_decimal("1 234,5", "x")) == "1234.5"
    assert parse_decimal("", "x") is None and parse_decimal(None, "x") is None
    with pytest.raises(RowError):
        parse_decimal("abc", "x")
    assert norm_id(11111.0, "x") == "11111"
    assert norm_id("ABCDEF0123456789ABCDEF0123456789", "x") == "abcdef01-2345-6789-abcd-ef0123456789"


def test_quantity_and_price_rules():
    r = run([
        {"product_id": "a", "store_id": "s", "qty": -3, "price": 0},       # qty->0, price игнор. => только остаток
        {"product_id": "b", "store_id": "s", "qty": "2,7", "price": 100},  # дробное -> 2
        {"product_id": "c", "store_id": "s", "price": 100, "old_price": 90},   # старая <= новой -> None
        {"product_id": "d", "store_id": "s", "price": "100", "old_price": "150"},
    ])
    by = {i["product_external_id"]: i for i in r.items}
    assert by["a"]["quantity"] == 0 and by["a"]["price"] is None
    assert by["b"]["quantity"] == 2
    assert by["c"]["old_price"] is None and by["c"]["quantity"] is None
    assert by["d"]["old_price"] == "150.00"
    assert r.warnings["negative_quantity_to_zero"] == 1
    assert r.warnings["zero_price_ignored"] == 1
    assert r.warnings["fractional_quantity_floored"] == 1
    assert r.warnings["old_price_dropped"] == 1


def test_bad_rows_are_rejected_not_fatal():
    r = run([
        {"product_id": "ok", "store_id": "s", "qty": 1},
        "строка-не-объект",
        {"store_id": "s", "qty": 1},                       # нет товара
        {"product_id": "x", "store_id": "s"},               # нет ни остатка, ни цены
        {"product_id": "y", "store_id": "s", "qty": "много"},
        {"product_id": "z", "store_id": "s", "price": 10**9},
        {"product_id": "w", "store_id": "s", "qty": 1, "currency": "USD"},
    ])
    assert len(r.items) == 1 and len(r.rejected) == 6 and r.error is None
    reasons = " | ".join(x["reason"] for x in r.rejected)
    assert "не является объектом" in reasons and "поля строки" in reasons and "неизвестная валюта" in reasons


def test_duplicates_last_wins():
    r = run([{"product_id": "p", "store_id": "s", "qty": 1}, {"product_id": "p", "store_id": "s", "qty": 9}])
    assert len(r.items) == 1 and r.items[0]["quantity"] == 9 and r.warnings["duplicates_in_batch"] == 1


def test_batch_level_errors():
    assert "Поля верхнего уровня" in run({"foo": 1}).error
    assert run("строка").error
    many = [{"product_id": str(i), "store_id": "s", "qty": 1} for i in range(5)]
    assert "максимум" in run(many, max_items=3).error


def test_full_mode_meta():
    r = run({"batch_id": "B1", "mode": "full", "final": "Да", "stores": [GUID.upper()], "items": []})
    assert (r.batch_id, r.mode, r.final, r.stores) == ("B1", "full", True, [GUID])
    assert run({"mode": "full", "items": []}).error  # без batch_id нельзя
    assert run({"mode": "wat", "items": []}).error


def test_extra_aliases():
    n = Normalizer({"product": ["КодТовара1С"], "quantity": ["КолВо"]})
    r = n.normalize([{"КодТовара1С": "p", "store_id": "s", "КолВо": 4}], 10)
    assert r.items[0]["quantity"] == 4
