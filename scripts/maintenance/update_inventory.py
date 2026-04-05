"""
GetLiveBugs.com - Inventory Updater & Change Detector
Diffs scraped_inventory.json against current_inventory.json.
Outputs: current_inventory.json, price_history.csv, changelog.csv, new_products.csv
"""

import json
import csv
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPED_FILE = os.path.join(SCRIPT_DIR, 'scraped_inventory.json')
CURRENT_FILE = os.path.join(SCRIPT_DIR, 'current_inventory.json')
PRICE_HISTORY_FILE = os.path.join(SCRIPT_DIR, 'price_history.csv')
CHANGELOG_FILE = os.path.join(SCRIPT_DIR, 'changelog.csv')
NEW_PRODUCTS_FILE = os.path.join(SCRIPT_DIR, 'new_products.csv')

MIN_PRICE = 0.50
MAX_PRICE = 5000.00
SUSPICIOUS_CHANGE_PCT = 0.50
MEANINGFUL_PRICE_DIFF = 1.00


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def append_csv(path, rows, fieldnames):
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def is_price_valid(price):
    if price is None:
        return True
    return MIN_PRICE <= price <= MAX_PRICE


def detect_changes(current_products, new_products, supplier_name, timestamp):
    changelog = []
    price_history = []
    new_entries = []

    current_by_id = {p['id']: p for p in current_products}
    new_by_id = {p['id']: p for p in new_products}

    for pid, new_p in new_by_id.items():
        if pid in current_by_id:
            old_p = current_by_id[pid]
            old_price = old_p.get('price')
            new_price = new_p.get('price')

            if old_price is not None and new_price is not None:
                diff = abs(new_price - old_price)
                if diff >= MEANINGFUL_PRICE_DIFF:
                    pct_change = diff / old_price if old_price > 0 else 0
                    suspicious = pct_change > SUSPICIOUS_CHANGE_PCT

                    if not is_price_valid(new_price):
                        new_p['price'] = old_price
                        changelog.append({
                            'timestamp': timestamp, 'supplier': supplier_name,
                            'product_id': pid, 'product_name': new_p['product_name'],
                            'change_type': 'price_invalid',
                            'old_value': str(old_price), 'new_value': str(new_price),
                            'flag': 'SKIPPED',
                        })
                    else:
                        changelog.append({
                            'timestamp': timestamp, 'supplier': supplier_name,
                            'product_id': pid, 'product_name': new_p['product_name'],
                            'change_type': 'price_change',
                            'old_value': f"${old_price:.2f}", 'new_value': f"${new_price:.2f}",
                            'flag': 'SUSPICIOUS' if suspicious else '',
                        })
                        price_history.append({
                            'timestamp': timestamp, 'supplier': supplier_name,
                            'product_id': pid, 'product_name': new_p['product_name'],
                            'old_price': old_price, 'new_price': new_price,
                            'change_pct': round(pct_change * 100, 1),
                        })

            old_avail = old_p.get('available')
            new_avail = new_p.get('available')
            if old_avail != new_avail:
                status = 'back_in_stock' if new_avail else 'sold_out'
                changelog.append({
                    'timestamp': timestamp, 'supplier': supplier_name,
                    'product_id': pid, 'product_name': new_p['product_name'],
                    'change_type': status,
                    'old_value': str(old_avail), 'new_value': str(new_avail),
                    'flag': '',
                })
        else:
            new_entries.append({
                'timestamp': timestamp, 'supplier': supplier_name,
                'product_id': pid, 'product_name': new_p['product_name'],
                'price': new_p.get('price', ''),
                'product_type': new_p.get('product_type', ''),
                'tags': ', '.join(new_p.get('tags', [])),
                'url': new_p.get('url', ''),
            })
            changelog.append({
                'timestamp': timestamp, 'supplier': supplier_name,
                'product_id': pid, 'product_name': new_p['product_name'],
                'change_type': 'new_product',
                'old_value': '', 'new_value': f"${new_p.get('price', 'N/A')}",
                'flag': '',
            })

    for pid, old_p in current_by_id.items():
        if pid not in new_by_id:
            changelog.append({
                'timestamp': timestamp, 'supplier': supplier_name,
                'product_id': pid, 'product_name': old_p['product_name'],
                'change_type': 'removed',
                'old_value': f"${old_p.get('price', 'N/A')}", 'new_value': '',
                'flag': '',
            })

    return changelog, price_history, new_entries


def main():
    print("GetLiveBugs.com - Inventory Updater")
    print("=" * 50)

    scraped = load_json(SCRAPED_FILE)
    if not scraped:
        print("ERROR: No scraped_inventory.json found. Run scrape_shopify.py first.")
        return

    current = load_json(CURRENT_FILE)
    if not current:
        current = {'last_updated': None, 'suppliers': {}}
        print("No existing inventory — starting fresh")

    timestamp = scraped.get('scraped_at', datetime.now(timezone.utc).isoformat())

    all_changelog = []
    all_price_history = []
    all_new_products = []

    for slug, supplier_data in scraped.get('suppliers', {}).items():
        name = supplier_data['name']
        status = supplier_data.get('status', 'error')

        if status in ('error', 'empty'):
            print(f"  {name}: {status.upper()} — keeping existing data")
            all_changelog.append({
                'timestamp': timestamp, 'supplier': name,
                'product_id': '', 'product_name': '',
                'change_type': f'supplier_{status}',
                'old_value': '', 'new_value': f'{status}, data preserved',
                'flag': 'WARNING',
            })
            continue

        new_products = supplier_data.get('products', [])
        current_products = current.get('suppliers', {}).get(slug, {}).get('products', [])

        changelog, price_history, new_entries = detect_changes(
            current_products, new_products, name, timestamp
        )

        all_changelog.extend(changelog)
        all_price_history.extend(price_history)
        all_new_products.extend(new_entries)

        current.setdefault('suppliers', {})[slug] = {
            'name': name,
            'category': supplier_data.get('category', ''),
            'product_count': supplier_data.get('product_count', 0),
            'in_stock_count': supplier_data.get('in_stock_count', 0),
            'avg_price': supplier_data.get('avg_price', 0),
            'last_scraped': timestamp,
            'products': new_products,
        }

        changes = len(changelog)
        print(f"  {name}: {len(new_products)} products, {changes} changes")

    current['last_updated'] = timestamp
    save_json(current, CURRENT_FILE)
    print(f"\nSaved inventory to {CURRENT_FILE}")

    if all_changelog:
        append_csv(CHANGELOG_FILE, all_changelog, [
            'timestamp', 'supplier', 'product_id', 'product_name',
            'change_type', 'old_value', 'new_value', 'flag',
        ])
        print(f"Appended {len(all_changelog)} changelog entries")

    if all_price_history:
        append_csv(PRICE_HISTORY_FILE, all_price_history, [
            'timestamp', 'supplier', 'product_id', 'product_name',
            'old_price', 'new_price', 'change_pct',
        ])
        print(f"Appended {len(all_price_history)} price changes")

    if all_new_products:
        append_csv(NEW_PRODUCTS_FILE, all_new_products, [
            'timestamp', 'supplier', 'product_id', 'product_name',
            'price', 'product_type', 'tags', 'url',
        ])
        print(f"Appended {len(all_new_products)} new product candidates")

    print()
    print("=" * 50)
    total_products = sum(s.get('product_count', 0) for s in current.get('suppliers', {}).values())
    total_in_stock = sum(s.get('in_stock_count', 0) for s in current.get('suppliers', {}).values())
    print(f"  Total products: {total_products}")
    print(f"  In stock: {total_in_stock}")
    print(f"  Suppliers: {len(current.get('suppliers', {}))}")


if __name__ == "__main__":
    main()
