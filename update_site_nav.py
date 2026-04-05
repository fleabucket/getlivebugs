"""
Quick script to update site-data.json categories/meta
and output updated Base.astro with new nav.

Run from project root:
  python3 update_site_nav.py
"""

import json, os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_PATH = os.path.join(PROJECT_ROOT, "src", "data", "site-data.json")

# Load site data
with open(SITE_DATA_PATH, 'r', encoding='utf-8') as f:
    site_data = json.load(f)

# Rebuild categories from actual species data
cat_counts = {}
cat_names = {}
for sp in site_data['species']:
    slug = sp['category_slug']
    name = sp['category']
    cat_counts[slug] = cat_counts.get(slug, 0) + 1
    cat_names[slug] = name

# Order: biggest/most important categories first
category_order = [
    'mantis', 'tarantula', 'isopod', 'jumping-spider',
    'scorpion', 'millipede', 'centipede', 'beetle',
    'roach', 'worm', 'stick-insect', 'moth'
]

categories = []
for slug in category_order:
    if slug in cat_counts:
        categories.append({
            "name": cat_names[slug],
            "slug": slug,
            "count": cat_counts[slug]
        })

# Add any categories not in our order list
for slug in cat_counts:
    if slug not in category_order:
        categories.append({
            "name": cat_names[slug],
            "slug": slug,
            "count": cat_counts[slug]
        })

site_data['categories'] = categories

# Update meta
supplier_set = set()
for sp in site_data['species']:
    for s in sp.get('suppliers', []):
        supplier_set.add(s.get('breeder', ''))
supplier_set.discard('')

site_data['meta'] = {
    "total_species": len(site_data['species']),
    "total_suppliers": len(supplier_set) if supplier_set else site_data.get('meta', {}).get('total_suppliers', 7),
}

# Save
with open(SITE_DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(site_data, f, indent=2, ensure_ascii=False)

print(f"✓ Updated site-data.json")
print(f"  Species: {site_data['meta']['total_species']}")
print(f"  Suppliers: {site_data['meta']['total_suppliers']}")
print(f"  Categories: {len(categories)}")
for cat in categories:
    print(f"    {cat['name']}: {cat['count']} species → /{cat['slug']}/")

# Now update Base.astro
BASE_PATH = os.path.join(PROJECT_ROOT, "src", "layouts", "Base.astro")
with open(BASE_PATH, 'r', encoding='utf-8') as f:
    base = f.read()

# Replace nav links
old_nav = """        <ul class="nav-links">
          <li><a href="/mantis/">Mantis</a></li>
          <li><a href="/tarantula/">Tarantula</a></li>
          <li><a href="/scorpion/">Scorpion</a></li>
          <li><a href="/worm/">Worm</a></li>
        </ul>"""

new_nav = """        <ul class="nav-links">
          <li><a href="/mantis/">Mantis</a></li>
          <li><a href="/tarantula/">Tarantula</a></li>
          <li><a href="/isopod/">Isopod</a></li>
          <li><a href="/jumping-spider/">Jumping Spider</a></li>
          <li><a href="/scorpion/">Scorpion</a></li>
          <li><a href="/worm/">Worm</a></li>
        </ul>"""

base = base.replace(old_nav, new_nav)

# Replace footer categories
old_footer_cats = """          <h4>Categories</h4>
          <ul>
            <li><a href="/mantis/">Praying Mantis</a></li>
            <li><a href="/tarantula/">Tarantulas</a></li>
            <li><a href="/scorpion/">Scorpions</a></li>
            <li><a href="/worm/">Worms</a></li>
          </ul>"""

new_footer_cats = """          <h4>Categories</h4>
          <ul>
            <li><a href="/mantis/">Praying Mantis</a></li>
            <li><a href="/tarantula/">Tarantulas</a></li>
            <li><a href="/isopod/">Isopods</a></li>
            <li><a href="/jumping-spider/">Jumping Spiders</a></li>
            <li><a href="/scorpion/">Scorpions</a></li>
            <li><a href="/millipede/">Millipedes</a></li>
            <li><a href="/centipede/">Centipedes</a></li>
            <li><a href="/beetle/">Beetles</a></li>
            <li><a href="/roach/">Roaches</a></li>
            <li><a href="/worm/">Worms</a></li>
            <li><a href="/stick-insect/">Stick Insects</a></li>
            <li><a href="/moth/">Moths</a></li>
          </ul>"""

base = base.replace(old_footer_cats, new_footer_cats)

with open(BASE_PATH, 'w', encoding='utf-8') as f:
    f.write(base)

print(f"\n✓ Updated Base.astro")
print(f"  Nav: added Isopod, Jumping Spider")
print(f"  Footer: all 12 categories listed")
print(f"\nRun: npm run build && git add . && git commit -m 'Update nav and categories' && git push")
