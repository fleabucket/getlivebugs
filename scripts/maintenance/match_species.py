"""
GetLiveBugs.com - Species Matcher
Connects scraped products from current_inventory.json to species in site-data.json.
Updates suppliers, prices, and stock counts for each species.

Run after update_inventory.py:
  python3 match_species.py
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_FILE = os.path.join(SCRIPT_DIR, 'current_inventory.json')
SITE_DATA_FILE = os.path.join(SCRIPT_DIR, '..', '..', 'src', 'data', 'site-data.json')



ALIASES = {
    "Antilles Pinktoe Tarantula": ["antilles pink toe", "caribena versicolor"],
    "Pink Toe Tarantula": ["pink toe tarantula", "avicularia avicularia"],
    "Salmon Pink Birdeater": ["salmon pink bird eater", "lasiodora parahybana"],
    "Bold Jumping Spider": ["phidippus audax", "bold jumping"],
    "Tan Jumping Spider": ["platycryptus undatus"],
    "Brilliant Jumping Spider": ["phidippus clarus"],
    "Canopy Jumping Spider": ["phidippus otiosus"],
    "Spiny Flower Mantis": ["spiny flower", "pseudocreobotra"],
    "Hooded Mantis": ["rhombodera fusca"],
    "Egyptian Pygmy Mantis": ["miomantis paykullii"],
    "Madagascar Hissing Cockroach": ["hissing cockroach", "gromphadorhina portentosa"],
    "Goliath Birdeater": ["goliath bird eater", "theraphosa blondi"],
    "Luna Moth": ["actias luna", "luna moth cocoon"],
    "Brunner's Stick Mantis": ["brunneria borealis"],
}

def normalize(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_match_keys(species):
    """Build a list of search strings for a species."""
    keys = []

    common = species.get('common_name', '')
    scientific = species.get('scientific_name', '')

    # Full common name: "Rubber Ducky Isopod"
    if common:
        keys.append(normalize(common))

    # Common name without category suffix: "Rubber Ducky"
    suffixes = ['isopod', 'tarantula', 'scorpion', 'mantis', 'millipede',
                'centipede', 'beetle', 'roach', 'cockroach', 'spider',
                'moth', 'worm', 'insect']
    common_norm = normalize(common)
    for suffix in suffixes:
        if common_norm.endswith(' ' + suffix):
            trimmed = common_norm[: -(len(suffix) + 1)].strip()
            if len(trimmed) > 2:
                keys.append(trimmed)
            break

    # Scientific name: "Cubaris sp. Rubber Ducky" or "Phidippus regius"
    if scientific:
        sci_norm = normalize(scientific)
        keys.append(sci_norm)
        # Also try just the genus + species (first two words)
        parts = sci_norm.split()
        if len(parts) == 2:
            keys.append(parts[0] + ' ' + parts[1])

    # Handle compound words
    for key in list(keys):
        if "birdeater" in key: keys.append(key.replace("birdeater", "bird eater"))
        if "bird eater" in key: keys.append(key.replace("bird eater", "birdeater"))
        if "pinktoe" in key: keys.append(key.replace("pinktoe", "pink toe"))
        if "pink toe" in key: keys.append(key.replace("pink toe", "pinktoe"))
    # Add manual aliases
    common = species.get("common_name", "")
    if common in ALIASES:
        keys.extend(ALIASES[common])
    return list(set(keys))


def product_matches_species(product_name, match_keys):
    """Check if a product name matches any of the species' keys."""
    prod_norm = normalize(product_name)

    for key in match_keys:
        if len(key) < 3:
            continue
        # Check if the key appears as a substring in the product name
        if key in prod_norm:
            return True
        # Check if the product name appears in the key
        if prod_norm in key:
            return True

    return False


def is_live_animal(product):
    """Filter out supplies, enclosures, and non-animal products."""
    name = product.get('product_name', '').lower()
    product_type = product.get('product_type', '').lower()
    tags = [t.lower() for t in product.get('tags', [])]

    # Exclude common non-animal products
    exclude_words = ['enclosure', 'terrarium', 'substrate', 'cage', 'habitat',
                     'book', 'poster', 'shirt', 't-shirt', 'tee', 'hoodie',
                     'sticker', 'enamel pin', 'lapel pin', 'mug', 'art print', 'decal', 'kit',
                     'supplement', 'vitamin', 'food', 'feeder', 'bedding',
                     'thermometer', 'hygrometer', 'heat mat', 'heat pad',
                     'water dish', 'hide', 'cork', 'moss', 'leaf litter',
                     'tongs', 'spray bottle', 'misting', 'light', 'lamp',
                     'gift card', 'bundle', 'combo pack', 'starter kit',
                     'plant', 'pothos', 'bamboo', 'monstera', 'fittonia',
                     'succulent', 'dracaena', 'fern', 'net cage', 'popup cage',
                     'plug', 'foam', 'trap', 'spray']

    for word in exclude_words:
        if word in name:
            return False

    return True


def main():
    print("GetLiveBugs.com - Species Matcher")
    print("=" * 50)

    # Load data
    if not os.path.exists(INVENTORY_FILE):
        print(f"ERROR: {INVENTORY_FILE} not found. Run scraper first.")
        return

    if not os.path.exists(SITE_DATA_FILE):
        print(f"ERROR: {SITE_DATA_FILE} not found.")
        return

    with open(INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)

    with open(SITE_DATA_FILE, 'r') as f:
        site_data = json.load(f)

    # Build all products list with supplier info
    all_products = []
    for slug, supplier_data in inventory.get('suppliers', {}).items():
        supplier_name = supplier_data.get('name', slug)
        for product in supplier_data.get('products', []):
            product['_supplier_name'] = supplier_name
            product['_supplier_slug'] = slug
            all_products.append(product)

    print(f"  Products loaded: {len(all_products)}")
    print(f"  Species to match: {len(site_data.get('species', []))}")
    print()

    # Match each species
    total_matched = 0
    total_suppliers = 0

    for species in site_data.get('species', []):
        match_keys = build_match_keys(species)
        matched_products = []

        for product in all_products:
            if not is_live_animal(product):
                continue
            if product_matches_species(product.get('product_name', ''), match_keys):
                matched_products.append(product)

        # Deduplicate by supplier (keep cheapest per supplier)
        by_supplier = {}
        for p in matched_products:
            sup = p['_supplier_name']
            price = p.get('price')
            if sup not in by_supplier:
                by_supplier[sup] = p
            elif price and (not by_supplier[sup].get('price') or price < by_supplier[sup]['price']):
                by_supplier[sup] = p

        # Build supplier list for this species
        suppliers = []
        for sup_name, p in by_supplier.items():
            suppliers.append({
                'breeder': sup_name,
                'product_name': p.get('product_name', ''),
                'price': p.get('price'),
                'available': p.get('available', False),
                'url': p.get('url', ''),
            })

        # Sort: in-stock first, then by price
        suppliers.sort(key=lambda s: (
            0 if s['available'] else 1,
            s['price'] if s['price'] else 9999
        ))

        # Update species entry
        species['suppliers'] = suppliers
        species['supplier_count'] = len(suppliers)
        species['in_stock_count'] = sum(1 for s in suppliers if s['available'])

        # Best price from in-stock suppliers
        in_stock_prices = [s['price'] for s in suppliers if s['available'] and s['price'] and s['price'] > 0]
        species['best_price'] = min(in_stock_prices) if in_stock_prices else None

        if suppliers:
            total_matched += 1
            total_suppliers += len(suppliers)
            status = f"{len(suppliers)} suppliers, {species['in_stock_count']} in stock"
            if species['best_price']:
                status += f", from ${species['best_price']:.0f}"
            print(f"  ✓ {species['common_name']}: {status}")
        else:
            print(f"  ✗ {species['common_name']}: no matches")

    # Save updated site-data.json
    print()
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)

    print(f"Updated {SITE_DATA_FILE}")
    print()
    print("=" * 50)
    print(f"  Species with suppliers: {total_matched}/{len(site_data['species'])}")
    print(f"  Total supplier matches: {total_suppliers}")
    no_match = len(site_data['species']) - total_matched
    if no_match:
        print(f"  No matches: {no_match}")


if __name__ == "__main__":
    main()
