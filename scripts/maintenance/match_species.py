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

# Compound word aliases — maps alternative spellings to canonical forms
ALIASES = {
    'bird eater': 'birdeater',
    'birdeater': 'bird eater',
    'pink toe': 'pinktoe',
    'pinktoe': 'pink toe',
    'green bottle blue': 'gbb',
    'curly hair': 'curlyhair',
    'red knee': 'redknee',
    'red rump': 'redrump',
}

# Trimmed keys that are too generic to ever use as standalone match terms.
# These are common adjectives/nouns that appear in supply product names.
BLOCKED_TRIMMED_KEYS = {
    'ghost', 'bark', 'orchid', 'dead leaf', 'chinese', 'asian', 'african',
    'european', 'indian', 'vietnamese', 'brazilian', 'mexican', 'chilean',
    'colombian', 'costa rican', 'peruvian', 'ecuadorian', 'venezuelan',
    'giant', 'common', 'desert', 'jungle', 'forest', 'tropical', 'flat',
    'spiny', 'horned', 'stripe', 'striped', 'spotted', 'banded',
    'brown', 'green', 'blue', 'orange', 'red', 'black', 'white', 'gold',
    'pink', 'yellow', 'purple', 'ivory', 'smoky', 'tiger', 'zebra',
    'king', 'queen', 'emperor', 'warrior', 'titan',
    'powder', 'powder blue', 'powder orange',
}


def normalize(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_match_keys(species):
    """Build a list of search keys for a species.

    Returns list of (key, require_word_boundary) tuples.
    - Full common name + scientific name: substring match (reliable)
    - Trimmed common name: word-boundary match only (prevents false positives)
    """
    keys = []

    common = species.get('common_name', '')
    scientific = species.get('scientific_name', '')

    # Full common name: "Rubber Ducky Isopod" — substring match
    if common:
        keys.append((normalize(common), False))

    # Common name without category suffix: "Rubber Ducky"
    # Only used if long enough and not in the blocked list
    suffixes = ['isopod', 'tarantula', 'scorpion', 'mantis', 'millipede',
                'centipede', 'beetle', 'roach', 'cockroach', 'spider',
                'moth', 'worm', 'insect', 'stick insect']
    common_norm = normalize(common)
    for suffix in suffixes:
        if common_norm.endswith(' ' + suffix):
            trimmed = common_norm[: -(len(suffix) + 1)].strip()
            if len(trimmed) >= 8 and trimmed not in BLOCKED_TRIMMED_KEYS:
                keys.append((trimmed, True))
            break

    # Scientific name: "Cubaris sp. Rubber Ducky" or "Phidippus regius"
    if scientific:
        sci_norm = normalize(scientific)
        keys.append((sci_norm, False))
        # Genus + species epithet — but skip if epithet is just "sp"
        parts = sci_norm.split()
        if len(parts) >= 2 and parts[1] != 'sp':
            keys.append((parts[0] + ' ' + parts[1], False))

    # Add alias variants for common name
    common_lower = common.lower()
    for alias_from, alias_to in ALIASES.items():
        if alias_from in common_lower:
            variant = common_lower.replace(alias_from, alias_to)
            keys.append((normalize(variant), False))

    return keys


def product_matches_species(product_name, match_keys):
    """Check if a product name matches any of the species' keys."""
    prod_norm = normalize(product_name)

    for key, word_boundary in match_keys:
        if len(key) < 3:
            continue

        if word_boundary:
            # Word-boundary match: key must appear as whole words
            pattern = r'(?:^|\s)' + re.escape(key) + r'(?:\s|$)'
            if re.search(pattern, prod_norm):
                return True
        else:
            # Substring match for full names and scientific names
            if key in prod_norm:
                return True

    return False


def is_live_animal(product):
    """Filter out supplies, enclosures, and non-animal products."""
    name = product.get('product_name', '').lower()

    exclude_words = [
        # Enclosures & housing
        'enclosure', 'terrarium', 'vivarium', 'cage', 'habitat', 'aquarium',
        'tank', 'net cage', 'popup cage', 'acrylic case', 'formicarium',
        # Substrates & bedding
        'substrate', 'bedding', 'soil', 'coco fiber', 'coconut fiber',
        'peat moss', 'sphagnum',
        # Decor & hardscape
        'branch', 'manzanita', 'ghostwood', 'driftwood', 'cholla',
        'cork', 'bark', 'vine', 'moss', 'leaf litter', 'seed pod',
        'hide', 'cave', 'log', 'hollow', 'coconut half',
        'decoration', 'decor', 'ornament', 'background',
        # Plants
        'plant', 'pothos', 'bamboo', 'monstera', 'fittonia',
        'succulent', 'dracaena', 'fern', 'bromeliad', 'tillandsia',
        'philodendron', 'ivy', 'terrarium plant',
        # Food & supplements
        'supplement', 'vitamin', 'calcium', 'food', 'diet', 'treat',
        'feeder', 'gut load', 'nectar', 'jelly', 'protein',
        # Equipment & tools
        'thermometer', 'hygrometer', 'heat mat', 'heat pad', 'heat lamp',
        'water dish', 'spray bottle', 'misting', 'mister',
        'tongs', 'tweezers', 'forceps', 'light', 'lamp', 'led',
        'plug', 'foam', 'trap', 'spray', 'screen', 'mesh', 'lid',
        # Merch & non-animal
        'book', 'poster', 'shirt', 't-shirt', 'tee', 'hoodie', 'hat', 'cap',
        'sticker', 'enamel pin', 'lapel pin', 'keychain',
        'mug', 'print', 'decal', 'magnet', 'patch', 'art print',
        'plush', 'stuffed', 'toy', 'figurine', 'figure', 'model', 'replica',
        'crewneck', 'sweatshirt', 'apparel',
        # Bundles & gift cards
        'gift card', 'gift certificate', 'e-gift',
        'bundle', 'combo pack', 'starter kit', 'care kit',
        # Containers & shipping
        'shipping', 'container', 'deli cup',
    ]

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

    # Update meta counts
    all_supplier_names = set()
    for species in site_data.get('species', []):
        for s in species.get('suppliers', []):
            all_supplier_names.add(s['breeder'])
    site_data['meta']['total_suppliers'] = len(all_supplier_names)
    site_data['meta']['total_species'] = len(site_data['species'])

    # Save updated site-data.json
    print()
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)

    print(f"Updated {SITE_DATA_FILE}")
    print()
    print("=" * 50)
    print(f"  Species with suppliers: {total_matched}/{len(site_data['species'])}")
    print(f"  Total supplier matches: {total_suppliers}")
    print(f"  Unique suppliers on site: {len(all_supplier_names)}")
    no_match = len(site_data['species']) - total_matched
    if no_match:
        print(f"  No matches: {no_match}")


if __name__ == "__main__":
    main()
