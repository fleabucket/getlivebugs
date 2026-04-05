"""
GetLiveBugs.com - Automated Inventory Scraper
Supports Shopify (/products.json) and WooCommerce (Store API).
Captures variant details for per-unit pricing and size/sex data.
Outputs scraped_inventory.json for the updater to diff.
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
    suppliers = []
    for s in config.get('shopify', []):
        s['platform'] = 'shopify'
        suppliers.append(s)
    for s in config.get('woocommerce', []):
        s['platform'] = 'woocommerce'
        suppliers.append(s)
    return suppliers


def parse_variant_label(variant):
    """Build a human-readable label from Shopify variant options."""
    parts = []
    for i in range(1, 4):
        opt = variant.get(f'option{i}')
        if opt and opt.lower() not in ('default title', 'default', 'title'):
            parts.append(opt)
    return ' / '.join(parts) if parts else None


def scrape_shopify(supplier):
    """Scrape a Shopify store via /products.json API."""
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
                variants_raw = product.get('variants', [])

                # Build variant details
                variants = []
                prices = []
                for v in variants_raw:
                    try:
                        p = float(v.get('price', 0))
                    except (ValueError, TypeError):
                        p = 0
                    if p > 0:
                        prices.append(p)

                    label = parse_variant_label(v)
                    variants.append({
                        'label': label,
                        'price': p if p > 0 else None,
                        'available': v.get('available', False),
                    })

                price = min(prices) if prices else None
                available = any(v.get('available', False) for v in variants_raw)

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
                    'variant_count': len(variants_raw),
                    'variants': variants,
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


def scrape_woocommerce(supplier):
    """Scrape a WooCommerce store via the Store API (WC Blocks)."""
    base_url = supplier['base_url'].rstrip('/')
    all_products = []
    page = 1

    while page <= MAX_PAGES:
        url = f"{base_url}/wp-json/wc/store/v1/products?per_page=100&page={page}"
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            if not data or not isinstance(data, list):
                break

            for product in data:
                price = None
                prices_data = product.get('prices', {})
                price_str = prices_data.get('price', '0')
                minor_unit = prices_data.get('currency_minor_unit', 2)
                try:
                    price = int(price_str) / (10 ** minor_unit)
                    if price <= 0:
                        price = None
                except (ValueError, TypeError):
                    price = None

                available = product.get('is_in_stock', False)

                image_url = ''
                images = product.get('images', [])
                if images:
                    image_url = images[0].get('src', '') or images[0].get('thumbnail', '')

                slug = product.get('slug', '')
                permalink = product.get('permalink', '')
                product_id = f"{supplier['slug']}:{slug}"

                categories = product.get('categories', [])
                cat_names = [c.get('name', '') for c in categories]

                all_products.append({
                    'id': product_id,
                    'supplier': supplier['name'],
                    'supplier_slug': supplier['slug'],
                    'supplier_category': supplier.get('category', ''),
                    'product_name': product.get('name', ''),
                    'handle': slug,
                    'price': price,
                    'available': available,
                    'product_type': ', '.join(cat_names[:3]),
                    'tags': [],
                    'image_url': image_url,
                    'url': permalink or f"{base_url}/product/{slug}/",
                    'variant_count': len(product.get('variations', [])),
                    'variants': [],
                })

            if len(data) < 100:
                break
            page += 1
            time.sleep(1)

        except HTTPError as e:
            if e.code == 404:
                return scrape_woocommerce_legacy(supplier)
            elif e.code == 429:
                print(f"  429 rate limited, waiting 30s...")
                time.sleep(30)
                continue
            else:
                print(f"  HTTP {e.code}")
                return scrape_woocommerce_legacy(supplier)
        except URLError as e:
            print(f"  Connection error: {e.reason}")
            return None
        except Exception as e:
            print(f"  Error: {e}")
            return None

    return all_products


def scrape_woocommerce_legacy(supplier):
    """Fallback: try the older WC REST API v3."""
    base_url = supplier['base_url'].rstrip('/')
    all_products = []
    page = 1

    while page <= MAX_PAGES:
        url = f"{base_url}/wp-json/wc/v3/products?per_page=100&page={page}"
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            if not data or not isinstance(data, list):
                break

            for product in data:
                price = None
                price_str = product.get('price', '')
                try:
                    price = float(price_str)
                    if price <= 0:
                        price = None
                except (ValueError, TypeError):
                    price = None

                available = product.get('in_stock', product.get('stock_status', '') == 'instock')

                image_url = ''
                images = product.get('images', [])
                if images:
                    image_url = images[0].get('src', '')

                slug = product.get('slug', '')
                permalink = product.get('permalink', '')
                product_id = f"{supplier['slug']}:{slug}"

                categories = product.get('categories', [])
                cat_names = [c.get('name', '') for c in categories]

                all_products.append({
                    'id': product_id,
                    'supplier': supplier['name'],
                    'supplier_slug': supplier['slug'],
                    'supplier_category': supplier.get('category', ''),
                    'product_name': product.get('name', ''),
                    'handle': slug,
                    'price': price,
                    'available': available,
                    'product_type': ', '.join(cat_names[:3]),
                    'tags': [t.get('name', '') for t in product.get('tags', [])[:10]],
                    'image_url': image_url,
                    'url': permalink or f"{base_url}/product/{slug}/",
                    'variant_count': len(product.get('variations', [])),
                    'variants': [],
                })

            if len(data) < 100:
                break
            page += 1
            time.sleep(1)

        except HTTPError as e:
            if e.code in (401, 403, 404):
                print(f"  WC API not public ({e.code}), skipping")
                return []
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


def scrape_supplier(supplier):
    """Route to the correct scraper based on platform."""
    platform = supplier.get('platform', 'shopify')
    if platform == 'woocommerce':
        return scrape_woocommerce(supplier)
    else:
        return scrape_shopify(supplier)


def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'suppliers.json')
    suppliers = load_suppliers(config_path)

    shopify_count = sum(1 for s in suppliers if s['platform'] == 'shopify')
    woo_count = sum(1 for s in suppliers if s['platform'] == 'woocommerce')

    print("GetLiveBugs.com - Automated Inventory Scraper")
    print("=" * 50)
    print(f"Suppliers to scrape: {len(suppliers)} ({shopify_count} Shopify, {woo_count} WooCommerce)")
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
        platform = supplier.get('platform', 'shopify')
        tag = "[WC]" if platform == 'woocommerce' else ""
        print(f"[{i+1}/{len(suppliers)}] {name} {tag}...", end=" ", flush=True)

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
