"""
GetLiveBugs.com - Automated Shopify Inventory Scraper
Hits /products.json for every Shopify supplier in suppliers.json.
Outputs scraped_inventory.json for the updater to diff.
Runtime: ~2-3 minutes for 37 suppliers (3s delay between requests).
"""

import json
import time
import sys
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HEADERS = {
    'User-Agent': 'GetLiveBugs/1.0 (getlivebugs.com; automated inventory check)',
    'Accept': 'application/json',
}

DELAY_BETWEEN_SUPPLIERS = 3
REQUEST_TIMEOUT = 20
MAX_PAGES = 3


def load_suppliers(config_path="suppliers.json"):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('shopify', [])


def scrape_supplier(supplier):
    base_url = supplier['base_url'].rstrip('/')
    all_products = []
    page = 1

    while page <= MAX_PAGES:
        url = f"{base_url}/products.json?limit=250&page={page}"
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            products = data.get('products', [])
            if not products:
                break

            for product in products:
                price = None
                if product.get('variants'):
                    prices = []
                    for v in product['variants']:
                        try:
                            p = float(v.get('price', 0))
                            if p > 0:
                                prices.append(p)
                        except (ValueError, TypeError):
                            continue
                    if prices:
                        price = min(prices)

                available = any(
                    v.get('available', False)
                    for v in product.get('variants', [])
                )

                image_url = ''
                if product.get('images'):
                    image_url = product['images'][0].get('src', '')

                product_id = f"{supplier['slug']}:{product.get('handle', '')}"

                all_products.append({
                    'id': product_id,
                    'supplier': supplier['name'],
                    'supplier_slug': supplier['slug'],
                    'supplier_category': supplier.get('category', ''),
                    'product_name': product.get('title', ''),
                    'handle': product.get('handle', ''),
                    'price': price,
                    'available': available,
                    'product_type': product.get('product_type', ''),
                    'tags': product.get('tags', [])[:10],
                    'image_url': image_url,
                    'url': f"{base_url}/products/{product.get('handle', '')}",
                    'variant_count': len(product.get('variants', [])),
                })

            if len(products) < 250:
                break
            page += 1
            time.sleep(1)

        except HTTPError as e:
            if e.code == 429:
                print(f"  429 rate limited, waiting 30s...")
                time.sleep(30)
                continue
            else:
                print(f"  HTTP {e.code}")
                return None
        except URLError as e:
            print(f"  Connection error: {e.reason}")
            return None
        except Exception as e:
            print(f"  Error: {e}")
            return None

    return all_products


def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'suppliers.json')
    suppliers = load_suppliers(config_path)

    print("GetLiveBugs.com - Automated Shopify Scraper")
    print("=" * 50)
    print(f"Suppliers to scrape: {len(suppliers)}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    results = {
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'suppliers': {},
        'summary': {
            'total_suppliers': len(suppliers),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_products': 0,
        },
    }

    for i, supplier in enumerate(suppliers):
        name = supplier['name']
        print(f"[{i+1}/{len(suppliers)}] {name}...", end=" ", flush=True)

        products = scrape_supplier(supplier)

        if products is None:
            print("FAILED")
            results['summary']['failed'] += 1
            results['suppliers'][supplier['slug']] = {
                'name': name, 'status': 'error', 'product_count': 0, 'products': [],
            }
        elif len(products) == 0:
            print("0 products")
            results['summary']['skipped'] += 1
            results['suppliers'][supplier['slug']] = {
                'name': name, 'status': 'empty', 'product_count': 0, 'products': [],
            }
        else:
            in_stock = sum(1 for p in products if p['available'])
            avg_items = [p['price'] for p in products if p['price'] and p['price'] > 0]
            avg_price = sum(avg_items) / len(avg_items) if avg_items else 0
            print(f"{len(products)} products ({in_stock} in stock, avg ${avg_price:.2f})")
            results['summary']['successful'] += 1
            results['summary']['total_products'] += len(products)
            results['suppliers'][supplier['slug']] = {
                'name': name, 'status': 'ok',
                'product_count': len(products), 'in_stock_count': in_stock,
                'avg_price': round(avg_price, 2), 'products': products,
            }

        if i < len(suppliers) - 1:
            time.sleep(DELAY_BETWEEN_SUPPLIERS)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_inventory.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 50)
    print(f"Done! {results['summary']['successful']} OK, "
          f"{results['summary']['failed']} failed, "
          f"{results['summary']['skipped']} empty")
    print(f"Total products: {results['summary']['total_products']}")
    print(f"Saved to: {output_path}")

    fail_rate = results['summary']['failed'] / max(results['summary']['total_suppliers'], 1)
    if fail_rate > 0.5:
        print(f"\nWARNING: {fail_rate:.0%} failure rate")
        sys.exit(1)


if __name__ == "__main__":
    main()
