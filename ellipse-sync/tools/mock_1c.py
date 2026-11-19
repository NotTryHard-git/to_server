"""
Эмулятор 1С: шлёт в ellipse-sync запросы так, как это МОГЛА бы делать реальная 1С —
в том числе «неряшливо» (запятые в числах, GUID в разном регистре, кириллические
имена полей, cp1251, мусорные строки). Нужен, чтобы проверить сервис ДО того, как
будет готова настоящая выгрузка, и чтобы специалист 1С мог сравнить свой формат.

Примеры (из папки ellipse-sync, сервисы запущены):
    python tools/mock_1c.py --key <SYNC_API_KEY> clean
    python tools/mock_1c.py --key <SYNC_API_KEY> --products-csv ../out/products_ready.csv \\
        --stores-csv ../stores_map.csv sloppy
    python tools/mock_1c.py --key <SYNC_API_KEY> full        # полная выгрузка в 3 пачки
    python tools/mock_1c.py --key <SYNC_API_KEY> load --rows 5000
    python tools/mock_1c.py --key <SYNC_API_KEY> status

Сценарии: clean, sloppy, cyrillic, grouped, bad, notjson, cp1251, full, load, status.
Запускается без сторонних зависимостей (только стандартная библиотека).
"""
import argparse
import base64
import csv
import json
import random
import sys
import time
import urllib.error
import urllib.request
import uuid


def load_ids(path: str | None, column: str, fallback_prefix: str, count: int) -> list[str]:
    if path:
        with open(path, encoding="utf-8-sig", newline="") as f:
            ids = [r[column].strip() for r in csv.DictReader(f) if r.get(column, "").strip()]
        if ids:
            return ids
        sys.exit(f"В {path} нет заполненной колонки {column}")
    return [str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{fallback_prefix}-{i}")) for i in range(count)]


def call(args, method: str, path: str, body: bytes | None = None, content_type="application/json; charset=utf-8"):
    headers = {"Content-Type": content_type}
    if args.auth == "apikey":
        headers["X-Api-Key"] = args.key
    elif args.auth == "bearer":
        headers["Authorization"] = f"Bearer {args.key}"
    else:  # basic — как у штатных HTTP-сервисов 1С
        headers["Authorization"] = "Basic " + base64.b64encode(f"1c:{args.key}".encode()).decode()
    request = urllib.request.Request(args.url.rstrip("/") + path, data=body, method=method, headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            status, text = response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status, text = exc.code, exc.read().decode("utf-8", errors="replace")
    elapsed = time.perf_counter() - started
    try:
        text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except ValueError:
        pass
    print(f"HTTP {status}  ({elapsed:.2f} с)\n{text}\n")
    return status


def send_json(args, payload, **kw):
    return call(args, "POST", "/sync/inventory-prices", json.dumps(payload, ensure_ascii=False).encode("utf-8"), **kw)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenario", choices=["clean", "sloppy", "cyrillic", "grouped", "bad", "notjson", "cp1251", "full", "load", "status"])
    parser.add_argument("--url", default="http://localhost:8001")
    parser.add_argument("--key", required=True, help="SYNC_API_KEY")
    parser.add_argument("--auth", choices=["apikey", "bearer", "basic"], default="apikey")
    parser.add_argument("--products-csv", help="CSV с колонкой external_id (например products_ready.csv)")
    parser.add_argument("--stores-csv", help="CSV с колонкой external_id (stores_map.csv)")
    parser.add_argument("--rows", type=int, default=20)
    args = parser.parse_args()

    products = load_ids(args.products_csv, "external_id", "product", max(args.rows, 50))
    stores = load_ids(args.stores_csv, "external_id", "store", 3)
    rnd = random.Random(42)

    def rows(n, per_store=None):
        picked = products[:n]
        return [(p, s) for s in (per_store or stores[:1]) for p in picked]

    if args.scenario == "status":
        call(args, "GET", "/sync/status")

    elif args.scenario == "clean":
        items = [{"product_external_id": p, "store_external_id": s, "quantity": rnd.randint(0, 30),
                  "price": round(rnd.uniform(200, 3000), 2), "old_price": None, "currency": "RUB"}
                 for p, s in rows(args.rows)]
        send_json(args, {"items": items})

    elif args.scenario == "sloppy":
        items = []
        for p, s in rows(args.rows):
            items.append({
                "product_external_id": p.upper() if rnd.random() < .5 else "{" + p + "}",
                "store_external_id": s.upper(),
                "quantity": rnd.choice([f"{rnd.randint(0, 30)}", f"{rnd.randint(0, 30)},0", rnd.randint(0, 30) + 0.0, -1]),
                "price": rnd.choice([f"{rnd.randint(1, 3):d} {rnd.randint(100, 999)},50 руб", f"{rnd.randint(200, 3000)}.5", 0]),
                "old_price": rnd.choice([None, "", "5 000,00"]),
                "currency": rnd.choice(["RUB", "руб.", "RUR"]),
            })
        send_json(args, {"data": items})

    elif args.scenario == "cyrillic":
        items = [{"Номенклатура": p, "Склад": s, "Остаток": rnd.randint(0, 30), "Цена": f"{rnd.randint(200, 3000)},00"}
                 for p, s in rows(args.rows)]
        send_json(args, {"Остатки": items})

    elif args.scenario == "grouped":
        send_json(args, {"items": [
            {"store_id": s, "items": [{"product_id": p, "qty": rnd.randint(0, 9), "price": 100 + i}
                                      for i, p in enumerate(products[:args.rows])]} for s in stores
        ]})

    elif args.scenario == "bad":
        send_json(args, [
            {"product_id": products[0], "store_id": stores[0], "qty": 3, "price": 100},
            "мусор", {"foo": "bar"}, {"product_id": products[1], "store_id": stores[0]},
            {"product_id": products[2], "store_id": stores[0], "qty": "много"},
        ])

    elif args.scenario == "notjson":
        call(args, "POST", "/sync/inventory-prices", b"<xml><item/></xml>", content_type="application/xml")

    elif args.scenario == "cp1251":
        body = json.dumps({"items": [{"product_id": products[0], "store_id": stores[0], "qty": 1, "price": 99}],
                           "comment": "Привет, Россия"}, ensure_ascii=False).encode("cp1251")
        call(args, "POST", "/sync/inventory-prices", body, content_type="application/json; charset=windows-1251")

    elif args.scenario == "full":
        batch_id = f"mock-full-{int(time.time())}"
        store = stores[0]
        pool = products[: args.rows]
        parts = [pool[i::3] for i in range(3)]
        for number, part in enumerate(parts, start=1):
            print(f"--- пачка {number}/3 (final={number == 3})")
            send_json(args, {"batch_id": batch_id, "mode": "full", "final": number == 3, "stores": [store],
                             "items": [{"product_external_id": p, "store_external_id": store,
                                        "quantity": rnd.randint(1, 20), "price": 500} for p in part]})

    elif args.scenario == "load":
        pool = (products * (args.rows // max(len(products), 1) + 1))[: args.rows]
        pool = list(dict.fromkeys(pool))
        step = 500
        for i in range(0, len(pool), step):
            chunk = pool[i : i + step]
            send_json(args, {"items": [{"product_external_id": p, "store_external_id": stores[0],
                                        "quantity": rnd.randint(0, 40), "price": round(rnd.uniform(100, 5000), 2)}
                                       for p in chunk]})


if __name__ == "__main__":
    main()
