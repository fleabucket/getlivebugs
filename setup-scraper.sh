#!/bin/bash
# GetLiveBugs.com — Scraper System Setup
# Run this from your repo root: bash setup-scraper.sh
set -e

echo ""
echo "====================================="
echo "  GetLiveBugs Scraper Setup"
echo "====================================="
echo ""

# Create directories
mkdir -p scripts/maintenance
mkdir -p .github/workflows

echo "Creating scripts/maintenance/suppliers.json..."
cat > scripts/maintenance/suppliers.json << 'SUPPLIERS_EOF'
{
  "shopify": [
    {
      "name": "PanTerra Pets",
      "slug": "panterra-pets",
      "base_url": "https://www.panterrapets.com",
      "category": "Exotic Pets",
      "specialties": ["mantis", "tarantula", "isopod", "millipede"]
    },
    {
      "name": "USMANTIS",
      "slug": "usmantis",
      "base_url": "https://usmantis.com",
      "category": "Exotic Pets",
      "specialties": ["mantis"]
    },
    {
      "name": "The Defiant Forest",
      "slug": "the-defiant-forest",
      "base_url": "https://www.thedefiantforest.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "tarantula", "millipede", "scorpion"]
    },
    {
      "name": "Exotics Unlimited",
      "slug": "exotics-unlimited",
      "base_url": "https://exoticsunlimitedusa.com",
      "category": "Exotic Pets",
      "specialties": ["tarantula", "scorpion", "centipede", "millipede"]
    },
    {
      "name": "Ty Dye Exotics",
      "slug": "ty-dye-exotics",
      "base_url": "https://tydyeexotic.com",
      "category": "Exotic Pets",
      "specialties": ["tarantula", "isopod", "scorpion"]
    },
    {
      "name": "Crown Bees",
      "slug": "crown-bees",
      "base_url": "https://crownbees.com",
      "category": "Beekeeping",
      "specialties": ["mason bee", "leafcutter bee"]
    },
    {
      "name": "Nature's Good Guys",
      "slug": "natures-good-guys",
      "base_url": "https://www.naturesgoodguys.com",
      "category": "Beneficial Insects",
      "specialties": ["ladybug", "lacewing", "nematode", "predatory mite"]
    },
    {
      "name": "Insect Lore",
      "slug": "insect-lore",
      "base_url": "https://www.insectlore.com",
      "category": "Educational Kits",
      "specialties": ["butterfly kit", "ladybug kit", "mantis kit"]
    },
    {
      "name": "Northwest Beneficials",
      "slug": "northwest-beneficials",
      "base_url": "https://nwbeneficials.com",
      "category": "Beneficial Insects",
      "specialties": ["ladybug", "lacewing", "predatory mite"]
    },
    {
      "name": "The Squirm Firm",
      "slug": "the-squirm-firm",
      "base_url": "https://thesquirmfirm.com",
      "category": "Worms",
      "specialties": ["red wiggler", "european nightcrawler"]
    },
    {
      "name": "Meme's Worms",
      "slug": "memes-worms",
      "base_url": "https://memesworms.com",
      "category": "Worms",
      "specialties": ["red wiggler", "european nightcrawler", "composting"]
    },
    {
      "name": "Rainbow Mealworms",
      "slug": "rainbow-mealworms",
      "base_url": "https://www.rainbowmealworms.net",
      "category": "Feeder Insects",
      "specialties": ["mealworm", "superworm", "cricket", "hornworm"]
    },
    {
      "name": "DubiaRoaches.com",
      "slug": "dubiaroaches",
      "base_url": "https://dubiaroaches.com",
      "category": "Feeder Insects",
      "specialties": ["dubia roach", "isopod", "cricket"]
    },
    {
      "name": "Top Hat Cricket Farm",
      "slug": "top-hat-cricket-farm",
      "base_url": "https://tophatcricketfarm.com",
      "category": "Feeder Insects",
      "specialties": ["cricket"]
    },
    {
      "name": "Symton Black Soldier Fly",
      "slug": "symton-bsf",
      "base_url": "https://symtonbsf.com",
      "category": "Feeder Insects",
      "specialties": ["black soldier fly larvae"]
    },
    {
      "name": "Flow Hive",
      "slug": "flow-hive",
      "base_url": "https://www.honeyflow.com",
      "category": "Beekeeping",
      "specialties": ["beehive", "beekeeping equipment"]
    },
    {
      "name": "Bee Built",
      "slug": "bee-built",
      "base_url": "https://www.beebuilt.com",
      "category": "Beekeeping",
      "specialties": ["beehive", "beekeeping equipment"]
    },
    {
      "name": "Clearwater Butterfly",
      "slug": "clearwater-butterfly",
      "base_url": "https://clearwaterbutterfly.com",
      "category": "Butterflies",
      "specialties": ["butterfly", "caterpillar", "butterfly release"]
    },
    {
      "name": "Shady Oak Butterfly Farm",
      "slug": "shady-oak-butterfly-farm",
      "base_url": "https://shadyoakbutterflyfarm.com",
      "category": "Butterflies",
      "specialties": ["butterfly", "caterpillar", "milkweed"]
    },
    {
      "name": "Lappe's Bee Supply",
      "slug": "lappes-bee-supply",
      "base_url": "https://www.lappesbeesupply.com",
      "category": "Beekeeping",
      "specialties": ["honey bee", "queen bee", "beekeeping equipment"]
    },
    {
      "name": "Fear Not Tarantulas",
      "slug": "fear-not-tarantulas",
      "base_url": "https://fearnottarantulas.com",
      "category": "Exotic Pets",
      "specialties": ["tarantula"]
    },
    {
      "name": "Exotics Source",
      "slug": "exotics-source",
      "base_url": "https://exoticssource.com",
      "category": "Exotic Pets",
      "specialties": ["jumping spider", "tarantula", "scorpion"]
    },
    {
      "name": "Spider Shoppe",
      "slug": "spider-shoppe",
      "base_url": "https://spidershoppe.com",
      "category": "Exotic Pets",
      "specialties": ["tarantula"]
    },
    {
      "name": "Isopod Shop",
      "slug": "isopod-shop",
      "base_url": "https://isopodshop.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "millipede"]
    },
    {
      "name": "Tropical Isopods",
      "slug": "tropical-isopods",
      "base_url": "https://tropicalisopods.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "springtail"]
    },
    {
      "name": "Holy-Poly Isopods",
      "slug": "holy-poly-isopods",
      "base_url": "https://holypolyisopods.com",
      "category": "Exotic Pets",
      "specialties": ["isopod"]
    },
    {
      "name": "Isopod Depot",
      "slug": "isopod-depot",
      "base_url": "https://isopoddepot.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "springtail"]
    },
    {
      "name": "Smug Bug",
      "slug": "smug-bug",
      "base_url": "https://smug-bug.com",
      "category": "Exotic Pets",
      "specialties": ["isopod"]
    },
    {
      "name": "US Invertebrate LLC",
      "slug": "us-invertebrate",
      "base_url": "https://usinvertebratellc.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "millipede"]
    },
    {
      "name": "The Spider Room",
      "slug": "the-spider-room",
      "base_url": "https://thespiderroom.com",
      "category": "Exotic Pets",
      "specialties": ["tarantula", "jumping spider", "scorpion"]
    },
    {
      "name": "Insect Sales",
      "slug": "insect-sales",
      "base_url": "https://insectsales.com",
      "category": "Exotic Pets",
      "specialties": ["jumping spider", "mantis", "ant", "worm", "millipede", "feeder"]
    },
    {
      "name": "Spoodville",
      "slug": "spoodville",
      "base_url": "https://spoodville.com",
      "category": "Exotic Pets",
      "specialties": ["jumping spider"]
    },
    {
      "name": "I Heart Bugs",
      "slug": "i-heart-bugs",
      "base_url": "https://iheartbugs.com",
      "category": "Exotic Pets",
      "specialties": ["isopod", "springtail"]
    },
    {
      "name": "Worm Nerd",
      "slug": "worm-nerd",
      "base_url": "https://wormnerd.com",
      "category": "Worms",
      "specialties": ["red wiggler", "worm castings", "composting"]
    },
    {
      "name": "Best Bee Brothers",
      "slug": "best-bee-brothers",
      "base_url": "https://bestbeebrothers.com",
      "category": "Pest Control",
      "specialties": ["carpenter bee trap", "wasp trap"]
    },
    {
      "name": "Praying Mantis Shop",
      "slug": "praying-mantis-shop",
      "base_url": "https://prayingmantisshop.com",
      "category": "Exotic Pets",
      "specialties": ["mantis"]
    },
    {
      "name": "MantisMart",
      "slug": "mantismart",
      "base_url": "https://www.mantismart.com",
      "category": "Exotic Pets",
      "specialties": ["mantis"]
    }
  ]
}
SUPPLIERS_EOF

echo "Creating scripts/maintenance/scrape_shopify.py..."
cat > scripts/maintenance/scrape_shopify.py << 'SCRAPER_EOF'
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
SCRAPER_EOF

echo "Creating scripts/maintenance/update_inventory.py..."
cat > scripts/maintenance/update_inventory.py << 'UPDATER_EOF'
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
UPDATER_EOF

echo "Creating scripts/maintenance/run_update.sh..."
cat > scripts/maintenance/run_update.sh << 'RUNNER_EOF'
#!/bin/bash
# Run inventory update locally
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "====================================="
echo "  GetLiveBugs Inventory Update"
echo "====================================="
echo ""
echo "Step 1/2: Scraping Shopify suppliers..."
echo ""
python3 scrape_shopify.py
echo ""
echo "Step 2/2: Detecting changes..."
echo ""
python3 update_inventory.py
echo ""
echo "Done! Check output files in scripts/maintenance/"
RUNNER_EOF
chmod +x scripts/maintenance/run_update.sh

echo "Creating scripts/maintenance/.gitignore..."
cat > scripts/maintenance/.gitignore << 'GITIGNORE_EOF'
# Temp staging file from scraper
scraped_inventory.json
GITIGNORE_EOF

echo "Creating .github/workflows/inventory-update.yml..."
cat > .github/workflows/inventory-update.yml << 'WORKFLOW_EOF'
name: Update Inventory

on:
  schedule:
    - cron: '0 6 * * 0'
  workflow_dispatch:

jobs:
  update-inventory:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run Shopify scraper
        working-directory: scripts/maintenance
        run: python scrape_shopify.py

      - name: Run inventory updater
        working-directory: scripts/maintenance
        run: python update_inventory.py

      - name: Commit and push changes
        run: |
          git config user.name "GetLiveBugs Bot"
          git config user.email "bot@getlivebugs.com"
          git add scripts/maintenance/current_inventory.json
          git add scripts/maintenance/price_history.csv
          git add scripts/maintenance/changelog.csv
          git add scripts/maintenance/new_products.csv
          git diff --staged --quiet || git commit -m "Inventory update $(date +%Y-%m-%d)"
          git push

      - name: Summary
        if: always()
        working-directory: scripts/maintenance
        run: |
          echo "## Inventory Update Results" >> $GITHUB_STEP_SUMMARY
          if [ -f current_inventory.json ]; then
            python -c "
          import json
          d = json.load(open('current_inventory.json'))
          print('| Supplier | Products | In Stock | Avg Price |')
          print('|----------|----------|----------|-----------|')
          for slug, s in sorted(d.get('suppliers', {}).items()):
              name = s.get('name', slug)
              count = s.get('product_count', 0)
              stock = s.get('in_stock_count', 0)
              avg = s.get('avg_price', 0)
              print(f'| {name} | {count} | {stock} | \${avg:.2f} |')
          " >> $GITHUB_STEP_SUMMARY
          fi
WORKFLOW_EOF

echo ""
echo "====================================="
echo "  Setup complete!"
echo "====================================="
echo ""
echo "Files created:"
echo "  scripts/maintenance/suppliers.json      (37 Shopify suppliers)"
echo "  scripts/maintenance/scrape_shopify.py    (scraper)"
echo "  scripts/maintenance/update_inventory.py  (change detector)"
echo "  scripts/maintenance/run_update.sh        (local runner)"
echo "  scripts/maintenance/.gitignore"
echo "  .github/workflows/inventory-update.yml   (weekly cron)"
echo ""
echo "To run your first scrape NOW:"
echo "  cd scripts/maintenance && bash run_update.sh"
echo ""
echo "To deploy the cron automation:"
echo "  git add -A && git commit -m 'Add automated scraper' && git push"
