"""
GetLiveBugs.com - Species Matcher (with enrichment)
Connects scraped products to species in site-data.json.
Extracts: size, sex, life stage, temperament, quantity, per-unit pricing
from product names, tags, and variant labels.

Run after update_inventory.py:
  python3 match_species.py
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_FILE = os.path.join(SCRIPT_DIR, 'current_inventory.json')
SITE_DATA_FILE = os.path.join(SCRIPT_DIR, '..', '..', 'src', 'data', 'site-data.json')

# ─── MATCHING CONFIG ─────────────────────────────────────────────

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

# ─── ATTRIBUTE EXTRACTION ────────────────────────────────────────

def extract_size(text):
    """Extract size measurement from text."""
    if not text:
        return None

    # Range: 3/4" - 1", 0.75"-1", 3-4 inches, 2" - 3"
    m = re.search(
        r'(?:about\s+|~\s*)?'
        r'(\d+(?:\.\d+)?(?:/\d+)?)\s*["\u201d]?\s*[-\u2013to]+\s*'
        r'(\d+(?:\.\d+)?(?:/\d+)?)\s*["\u201d]?(?:\s*inch(?:es)?)?',
        text, re.IGNORECASE
    )
    if m:
        return f'{m.group(1)}\u2013{m.group(2)}"'

    # Single fractional: 3/4", 1/2"
    m = re.search(r'(?:about\s+|~\s*)?(\d+\s*\d*/\d+)\s*["\u201d]', text)
    if m:
        return f'{m.group(1)}"'

    # Single decimal: 1.5", 0.75", but NOT things like ".5-.75" without leading digit
    m = re.search(r'(?:about\s+|~\s*)?(\d+\.?\d*)\s*["\u201d](?!\w)', text)
    if m:
        val = m.group(1)
        if float(val) < 30:  # sanity: no 250" spiders
            return f'{val}"'

    # "X inch" or "X inches"
    m = re.search(r'(?:about\s+|~\s*)?(\d+\.?\d*)\s*inch(?:es)?', text, re.IGNORECASE)
    if m:
        val = m.group(1)
        if float(val) < 30:
            return f'{val}"'

    # Centimeters
    m = re.search(r'(\d+(?:\.\d+)?(?:\s*[-\u2013]\s*\d+(?:\.\d+)?)?)\s*cm', text, re.IGNORECASE)
    if m:
        return f'{m.group(1)}cm'

    # Catch ".5-.75 inch" pattern (no leading digit before decimal)
    m = re.search(r'\.(\d+)\s*[-\u2013]\s*\.?(\d+\.?\d*)\s*(?:inch|")', text, re.IGNORECASE)
    if m:
        return f'0.{m.group(1)}\u20130.{m.group(2)}"'

    return None


def extract_life_stage(text, tags=None):
    """Extract life stage from product name and/or tags."""
    combined = (text or '').lower()
    if tags:
        combined += ' ' + ' '.join(t.lower() for t in tags)

    patterns = [
        (r'\bspiderling\b', 'Spiderling'),
        (r'\bsling\b', 'Sling'),
        (r'\bsub[\s-]?adult\b', 'Sub-adult'),
        (r'\bjuvenile\b', 'Juvenile'),
        (r'\bjuvie\b', 'Juvenile'),
        (r'\bnymph\b', 'Nymph'),
        (r'\bnewborn\b', 'Newborn'),
        (r'\bbaby\b', 'Baby'),
        (r'\badult\b', 'Adult'),
        (r'\bready to breed\b', 'Adult'),
        (r'\bbreeding\s+(?:size|age)\b', 'Adult'),
    ]

    for pattern, label in patterns:
        if re.search(pattern, combined):
            return label

    # Check tags specifically for "spiderlings" (plural form used as category tag)
    if tags:
        tag_lower = [t.lower() for t in tags]
        if 'spiderlings' in tag_lower or 'spiderling' in tag_lower:
            return 'Spiderling'

    # Instar notation: i2, i3, i4, L1, L2
    m = re.search(r'\b[iI](\d)\b', text or '')
    if m:
        return f'Instar {m.group(1)}'
    m = re.search(r'\b[lL](\d)\b', text or '')
    if m:
        return f'L{m.group(1)}'

    return None


def extract_sex(text):
    """Extract sex from product name."""
    if not text:
        return None
    text_lower = text.lower()

    if re.search(r'\bpair\b|\bduo\b|\bmated pair\b|\bbreeding pair\b', text_lower):
        return 'Pair'
    if re.search(r'\bfemale\b', text_lower):
        return 'Female'
    if re.search(r'\bmale\b', text_lower) and 'female' not in text_lower:
        return 'Male'
    if re.search(r'\bunsexed\b', text_lower):
        return 'Unsexed'

    return None


def extract_temperament(tags):
    """Extract temperament from product tags."""
    if not tags:
        return None
    tag_set = {t.lower().strip() for t in tags}

    if 'docile' in tag_set:
        return 'Docile'
    if 'skittish' in tag_set:
        return 'Skittish'
    if 'defensive' in tag_set:
        return 'Defensive'

    return None


def extract_world(tags):
    """Extract New World / Old World classification from tags."""
    if not tags:
        return None
    tag_set = {t.lower().strip() for t in tags}

    if 'new world' in tag_set:
        return 'New World'
    if 'old world' in tag_set:
        return 'Old World'

    return None


def extract_habitat_type(tags):
    """Extract terrestrial/arboreal from tags."""
    if not tags:
        return None
    tag_set = {t.lower().strip() for t in tags}

    if 'arboreal' in tag_set:
        return 'Arboreal'
    if 'terrestrial' in tag_set:
        return 'Terrestrial'

    return None


def extract_quantity(text, variants=None):
    """Extract pack quantity from product name or variant labels."""
    sources = [text or '']
    if variants:
        for v in variants:
            label = v.get('label', '')
            if label:
                sources.append(label)

    for src in sources:
        src_lower = src.lower()
        patterns = [
            r'(\d+)\s*(?:ct|count)\b',
            r'(\d+)\s*pack\b',
            r'(\d+)\s*mixed\b',
            r'\bx(\d+)\b',
            r'(\d+)\s*(?:pc|pcs|pieces?)\b',
            r'\b(\d+)\s*(?:lot|set)\b',
        ]
        for pattern in patterns:
            m = re.search(pattern, src_lower)
            if m:
                qty = int(m.group(1))
                if 2 <= qty <= 1000:
                    return qty

    return None


def build_variant_options(variants):
    """Build clean variant display options from raw variant data."""
    if not variants:
        return []

    options = []
    for v in variants:
        label = v.get('label')
        price = v.get('price')
        available = v.get('available', False)

        if not label or not price:
            continue

        # Skip "Default Title" type entries
        if label.lower() in ('default title', 'default', 'title'):
            continue

        options.append({
            'label': label,
            'price': price,
            'available': available,
        })

    return options


# ─── MATCHING LOGIC ──────────────────────────────────────────────

def normalize(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_match_keys(species):
    """Build search keys for species matching."""
    keys = []
    common = species.get('common_name', '')
    scientific = species.get('scientific_name', '')

    if common:
        keys.append((normalize(common), False))

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

    if scientific:
        sci_norm = normalize(scientific)
        keys.append((sci_norm, False))
        parts = sci_norm.split()
        if len(parts) >= 2 and parts[1] != 'sp':
            keys.append((parts[0] + ' ' + parts[1], False))

    common_lower = common.lower()
    for alias_from, alias_to in ALIASES.items():
        if alias_from in common_lower:
            variant = common_lower.replace(alias_from, alias_to)
            keys.append((normalize(variant), False))

    return keys


def product_matches_species(product_name, match_keys):
    """Check if a product matches a species."""
    prod_norm = normalize(product_name)

    for key, word_boundary in match_keys:
        if len(key) < 3:
            continue
        if word_boundary:
            pattern = r'(?:^|\s)' + re.escape(key) + r'(?:\s|$)'
            if re.search(pattern, prod_norm):
                return True
        else:
            if key in prod_norm:
                return True

    return False


def is_live_animal(product):
    """Filter out non-animal products."""
    name = product.get('product_name', '').lower()

    exclude_words = [
        'enclosure', 'terrarium', 'vivarium', 'cage', 'habitat', 'aquarium',
        'tank', 'net cage', 'popup cage', 'acrylic case', 'formicarium',
        'substrate', 'bedding', 'soil', 'coco fiber', 'coconut fiber',
        'peat moss', 'sphagnum',
        'branch', 'manzanita', 'ghostwood', 'driftwood', 'cholla',
        'cork', 'bark', 'vine', 'moss', 'leaf litter', 'seed pod',
        'hide', 'cave', 'log', 'hollow', 'coconut half',
        'decoration', 'decor', 'ornament', 'background',
        'plant', 'pothos', 'bamboo', 'monstera', 'fittonia',
        'succulent', 'dracaena', 'fern', 'bromeliad', 'tillandsia',
        'philodendron', 'ivy', 'terrarium plant',
        'supplement', 'vitamin', 'calcium', 'food', 'diet', 'treat',
        'feeder', 'gut load', 'nectar', 'jelly', 'protein',
        'thermometer', 'hygrometer', 'heat mat', 'heat pad', 'heat lamp',
        'water dish', 'spray bottle', 'misting', 'mister',
        'tongs', 'tweezers', 'forceps', 'light', 'lamp', 'led',
        'plug', 'foam', 'trap', 'spray', 'screen', 'mesh', 'lid',
        'book', 'poster', 'shirt', 't-shirt', 'tee', 'hoodie', 'hat', 'cap',
        'sticker', 'enamel pin', 'lapel pin', 'keychain',
        'mug', 'print', 'decal', 'magnet', 'patch', 'art print',
        'plush', 'stuffed', 'toy', 'figurine', 'figure', 'model', 'replica',
        'crewneck', 'sweatshirt', 'apparel',
        'gift card', 'gift certificate', 'e-gift',
        'bundle', 'combo pack', 'starter kit', 'care kit',
        'shipping', 'container', 'deli cup',
    ]

    for word in exclude_words:
        if word in name:
            return False

    return True


# ─── MAIN ────────────────────────────────────────────────────────

def main():
    print("GetLiveBugs.com - Species Matcher (enriched)")
    print("=" * 50)

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

    # Build products list
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

    total_matched = 0
    total_suppliers = 0
    enrichment_stats = {'size': 0, 'life_stage': 0, 'sex': 0, 'temperament': 0, 'quantity': 0}

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

        # Build enriched supplier list
        suppliers = []
        for sup_name, p in by_supplier.items():
            name = p.get('product_name', '')
            tags = p.get('tags', [])
            variants = p.get('variants', [])
            price = p.get('price')

            # Extract attributes
            size = extract_size(name)
            life_stage = extract_life_stage(name, tags)
            sex = extract_sex(name)
            temperament = extract_temperament(tags)
            world = extract_world(tags)
            habitat = extract_habitat_type(tags)
            quantity = extract_quantity(name, variants)

            # Also check variant labels for size/quantity
            if not size and variants:
                for v in variants:
                    label = v.get('label', '')
                    if label:
                        size = extract_size(label)
                        if size:
                            break

            # Per-unit pricing
            per_unit = None
            if price and quantity and quantity > 1:
                per_unit = round(price / quantity, 2)

            # Build variant options for display
            variant_options = build_variant_options(variants)

            # Track stats
            if size: enrichment_stats['size'] += 1
            if life_stage: enrichment_stats['life_stage'] += 1
            if sex: enrichment_stats['sex'] += 1
            if temperament: enrichment_stats['temperament'] += 1
            if quantity and quantity > 1: enrichment_stats['quantity'] += 1

            entry = {
                'breeder': sup_name,
                'product_name': name,
                'price': price,
                'available': p.get('available', False),
                'url': p.get('url', ''),
            }

            # Only include enrichment fields that have values
            if size:
                entry['size'] = size
            if life_stage:
                entry['life_stage'] = life_stage
            if sex:
                entry['sex'] = sex
            if temperament:
                entry['temperament'] = temperament
            if world:
                entry['world'] = world
            if habitat:
                entry['habitat'] = habitat
            if quantity and quantity > 1:
                entry['quantity'] = quantity
                entry['per_unit_price'] = per_unit
            if variant_options:
                entry['variants'] = variant_options

            suppliers.append(entry)

        # Sort: in-stock first, then by per-unit price (or price if no quantity)
        suppliers.sort(key=lambda s: (
            0 if s['available'] else 1,
            s.get('per_unit_price') or s['price'] if s['price'] else 9999
        ))

        # Update species entry
        species['suppliers'] = suppliers
        species['supplier_count'] = len(suppliers)
        species['in_stock_count'] = sum(1 for s in suppliers if s['available'])

        in_stock_prices = [s['price'] for s in suppliers if s['available'] and s['price'] and s['price'] > 0]
        species['best_price'] = min(in_stock_prices) if in_stock_prices else None

        if suppliers:
            total_matched += 1
            total_suppliers += len(suppliers)
            status = f"{len(suppliers)} suppliers, {species['in_stock_count']} in stock"
            if species['best_price']:
                status += f", from ${species['best_price']:.0f}"
            print(f"  \u2713 {species['common_name']}: {status}")
        else:
            print(f"  \u2717 {species['common_name']}: no matches")

    # Update meta
    all_supplier_names = set()
    for species in site_data.get('species', []):
        for s in species.get('suppliers', []):
            all_supplier_names.add(s['breeder'])
    site_data['meta']['total_suppliers'] = len(all_supplier_names)
    site_data['meta']['total_species'] = len(site_data['species'])

    # Save
    print()
    with open(SITE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)

    print(f"Updated {SITE_DATA_FILE}")
    print()
    print("=" * 50)
    print(f"  Species with suppliers: {total_matched}/{len(site_data['species'])}")
    print(f"  Total supplier matches: {total_suppliers}")
    print(f"  Unique suppliers on site: {len(all_supplier_names)}")
    print()
    print("  Enrichment coverage:")
    print(f"    Size:         {enrichment_stats['size']:>4} listings")
    print(f"    Life stage:   {enrichment_stats['life_stage']:>4} listings")
    print(f"    Sex:          {enrichment_stats['sex']:>4} listings")
    print(f"    Temperament:  {enrichment_stats['temperament']:>4} listings")
    print(f"    Quantity:     {enrichment_stats['quantity']:>4} listings")

    no_match = len(site_data['species']) - total_matched
    if no_match:
        print(f"  No matches: {no_match}")


if __name__ == "__main__":
    main()
