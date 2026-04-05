"""
GetLiveBugs.com — Add 32 New Species to Site
==============================================
1. Merges 32 new species + photos into site-data.json
2. Copies mantis page templates for 8 new categories (swapping category slug)

HOW TO RUN:
  cd ~/Desktop/getlivebugs
  python3 add_new_species.py

  Required files in project root:
  - new_species_for_site_data.json
  - new_species_photos.csv
  - remaining_photos.csv
"""

import json, csv, os, shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_DATA_PATH = os.path.join(PROJECT_ROOT, "src", "data", "site-data.json")
NEW_SPECIES_PATH = os.path.join(PROJECT_ROOT, "new_species_for_site_data.json")
PHOTOS_CSV = os.path.join(PROJECT_ROOT, "new_species_photos.csv")
REMAINING_CSV = os.path.join(PROJECT_ROOT, "remaining_photos.csv")
PAGES_DIR = os.path.join(PROJECT_ROOT, "src", "pages")
MANTIS_DIR = os.path.join(PAGES_DIR, "mantis")

def load_photos():
    photos = {}
    for csv_path in [PHOTOS_CSV, REMAINING_CSV]:
        if not os.path.exists(csv_path):
            print(f"  Warning: {os.path.basename(csv_path)} not found, skipping")
            continue
        with open(csv_path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                name = row['common_name']
                url = row.get('photo_url') or row.get('original_url', '')
                if url and row.get('source', '') != 'NONE':
                    photos[name] = url
    return photos

def copy_category_pages(category_slug):
    cat_dir = os.path.join(PAGES_DIR, category_slug)
    if os.path.exists(cat_dir):
        print(f"  Already exists: {category_slug}/ — skipping")
        return False
    shutil.copytree(MANTIS_DIR, cat_dir)
    for root, dirs, files in os.walk(cat_dir):
        for fname in files:
            if fname.endswith('.astro'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = content.replace(
                    "sp.category_slug === 'mantis'",
                    f"sp.category_slug === '{category_slug}'"
                )
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
    print(f"  ✓ Created: {category_slug}/ (copied from mantis)")
    return True

def main():
    print("GetLiveBugs.com — Add 32 New Species")
    print("=" * 45)
    missing = False
    for path, label in [(SITE_DATA_PATH, "src/data/site-data.json"), (NEW_SPECIES_PATH, "new_species_for_site_data.json"), (MANTIS_DIR, "src/pages/mantis/")]:
        if not os.path.exists(path):
            print(f"  ERROR: {label} not found")
            missing = True
    if missing:
        print("\nMake sure you're running from project root.")
        return

    print("\n1. Loading site-data.json...")
    with open(SITE_DATA_PATH, 'r', encoding='utf-8') as f:
        site_data = json.load(f)
    existing_slugs = {sp['slug'] for sp in site_data.get('species', [])}
    print(f"   Existing species: {len(existing_slugs)}")

    print("\n2. Loading new species content...")
    with open(NEW_SPECIES_PATH, 'r', encoding='utf-8') as f:
        new_species = json.load(f)
    print(f"   New species: {len(new_species)}")

    print("\n3. Attaching photos...")
    photos = load_photos()
    photo_count = 0
    for sp in new_species:
        if sp['common_name'] in photos:
            sp['photo_url'] = photos[sp['common_name']]
            photo_count += 1
    print(f"   Photos attached: {photo_count}/{len(new_species)}")

    print("\n4. Merging into site-data.json...")
    added = 0
    for sp in new_species:
        if sp['slug'] not in existing_slugs:
            site_data['species'].append(sp)
            existing_slugs.add(sp['slug'])
            added += 1
    print(f"   Added: {added}")
    print(f"   Total species now: {len(site_data['species'])}")

    print("\n5. Saving site-data.json...")
    backup = SITE_DATA_PATH + '.backup'
    shutil.copy2(SITE_DATA_PATH, backup)
    print(f"   Backup: {backup}")
    with open(SITE_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)
    print("   ✓ Saved")

    print("\n6. Creating page folders (copying from mantis template)...")
    new_cats = set()
    for sp in new_species:
        cs = sp['category_slug']
        if cs not in new_cats and not os.path.exists(os.path.join(PAGES_DIR, cs)):
            new_cats.add(cs)
            copy_category_pages(cs)
    if not new_cats:
        print("   All category folders already exist")

    print("\n" + "=" * 45)
    print("DONE!")
    print(f"\n  Species added: {added}")
    print(f"  Photos attached: {photo_count}")
    print(f"  New category folders: {len(new_cats)}")
    print(f"\nNEXT STEPS:")
    print(f"  1. Update nav in your layout to add new categories")
    print(f"  2. npm run build")
    print(f"  3. npm run dev  (preview at localhost)")
    print(f"  4. git add . && git commit -m 'Add 32 new species' && git push")
    print(f"  5. Submit key URLs to Search Console")

if __name__ == "__main__":
    main()
