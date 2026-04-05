"""
GetLiveBugs.com — Fallback Photo Finder for Isopod Morphs
==========================================================
Searches for photos of the 3 remaining species using:
1. iNaturalist search by base species (without morph name)
2. Wikimedia Commons keyword search
3. iNaturalist common name search

HOW TO RUN:
  python3 find_remaining_photos.py
"""

import requests
import csv
import time
import json

HEADERS = {
    'User-Agent': 'GetLiveBugs/1.0 (getlivebugs.com)',
}

MISSING_SPECIES = [
    {
        "common_name": "Rubber Ducky Isopod",
        "scientific_name": 'Cubaris sp. "Rubber Ducky"',
        "base_species": "Cubaris",
        "search_terms": ["Cubaris rubber ducky", "rubber ducky isopod", "Cubaris murina"],
    },
    {
        "common_name": "Dairy Cow Isopod",
        "scientific_name": "Porcellio laevis 'Dairy Cow'",
        "base_species": "Porcellio laevis",
        "search_terms": ["dairy cow isopod", "Porcellio laevis dairy cow", "Porcellio laevis"],
    },
    {
        "common_name": "Magic Potion Isopod",
        "scientific_name": "Armadillidium vulgare 'Magic Potion'",
        "base_species": "Armadillidium vulgare",
        "search_terms": ["magic potion isopod", "Armadillidium vulgare magic potion", "Armadillidium vulgare"],
    },
]


def search_inaturalist_by_name(query):
    """Search iNaturalist taxa by name."""
    try:
        response = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={'q': query, 'per_page': 5},
            headers=HEADERS,
            timeout=10
        )
        data = response.json()
        for taxon in data.get('results', []):
            photo = taxon.get('default_photo', {})
            if photo:
                license_code = photo.get('license_code', '')
                if license_code and license_code.lower() in ['cc-by', 'cc-by-sa', 'cc0']:
                    return {
                        'source': 'iNaturalist',
                        'photo_url': photo.get('medium_url', '').replace('medium', 'large'),
                        'original_url': photo.get('original_url', photo.get('medium_url', '').replace('medium', 'original')),
                        'attribution': photo.get('attribution', ''),
                        'license': license_code,
                        'note': f'Found via search: "{query}"',
                    }
    except Exception as e:
        print(f"    iNaturalist error: {e}")
    return None


def search_wikimedia_commons(query):
    """Search Wikimedia Commons for CC images."""
    try:
        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                'action': 'query',
                'generator': 'search',
                'gsrsearch': query,
                'gsrnamespace': 6,  # File namespace
                'gsrlimit': 5,
                'prop': 'imageinfo',
                'iiprop': 'url|extmetadata',
                'iiurlwidth': 800,
                'format': 'json',
            },
            headers=HEADERS,
            timeout=10
        )
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page in pages.items():
            imageinfo = page.get('imageinfo', [{}])[0]
            url = imageinfo.get('thumburl', imageinfo.get('url', ''))
            original = imageinfo.get('url', '')
            ext = page.get('title', '').lower()
            # Only want actual photos, not SVGs or icons
            if any(ext.endswith(x) for x in ['.jpg', '.jpeg', '.png']):
                metadata = imageinfo.get('extmetadata', {})
                license_name = metadata.get('LicenseShortName', {}).get('value', '')
                artist = metadata.get('Artist', {}).get('value', '')
                if any(cc in license_name.lower() for cc in ['cc', 'public domain', 'pd']):
                    return {
                        'source': 'Wikimedia Commons',
                        'photo_url': url,
                        'original_url': original,
                        'attribution': artist[:200] if artist else 'See Wikimedia Commons',
                        'license': license_name,
                        'note': f'Found via Commons search: "{query}"',
                    }
    except Exception as e:
        print(f"    Wikimedia error: {e}")
    return None


def search_flickr_public(query):
    """Search Flickr for CC-licensed photos (no API key needed)."""
    try:
        # Flickr has a public feed for CC-licensed content
        response = requests.get(
            "https://www.flickr.com/services/feeds/photos_public.gne",
            params={
                'tags': query.replace(' ', ','),
                'format': 'json',
                'nojsoncallback': 1,
                'license': '1,2,3,4,5,6',  # CC licenses
            },
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            for item in items:
                media = item.get('media', {})
                photo_url = media.get('m', '').replace('_m.', '_b.')
                if photo_url:
                    return {
                        'source': 'Flickr',
                        'photo_url': photo_url,
                        'original_url': item.get('link', ''),
                        'attribution': item.get('author', ''),
                        'license': 'CC (check original)',
                        'note': f'Found via Flickr search: "{query}"',
                    }
    except Exception as e:
        print(f"    Flickr error: {e}")
    return None


def main():
    print("GetLiveBugs.com — Fallback Photo Finder")
    print("=" * 45)
    print()

    results = []

    for species in MISSING_SPECIES:
        print(f"Searching for: {species['common_name']}")
        found = None

        for term in species['search_terms']:
            if found:
                break

            # Try Wikimedia Commons first (most likely to have hobby morphs)
            print(f"  Trying Wikimedia Commons: '{term}'...")
            found = search_wikimedia_commons(term)
            if found:
                print(f"  ✓ Found on Wikimedia Commons!")
                break
            time.sleep(1)

            # Try iNaturalist
            print(f"  Trying iNaturalist: '{term}'...")
            found = search_inaturalist_by_name(term)
            if found:
                print(f"  ✓ Found on iNaturalist!")
                break
            time.sleep(1)

        # Try Flickr as last resort
        if not found:
            for term in species['search_terms'][:2]:
                print(f"  Trying Flickr: '{term}'...")
                found = search_flickr_public(term)
                if found:
                    print(f"  ✓ Found on Flickr!")
                    break
                time.sleep(1)

        if found:
            found['common_name'] = species['common_name']
            found['scientific_name'] = species['scientific_name']
            results.append(found)
            print(f"  → {found['source']}: {found['photo_url'][:80]}...")
        else:
            print(f"  ✗ No CC photo found anywhere.")
            print(f"    Manual option: search flickr.com/search/?q={species['common_name'].replace(' ', '+')}&license=2%2C3%2C4%2C5%2C6")
            results.append({
                'common_name': species['common_name'],
                'scientific_name': species['scientific_name'],
                'source': 'NONE',
                'photo_url': '',
                'original_url': '',
                'attribution': '',
                'license': '',
                'note': 'Manual sourcing needed',
            })
        print()

    # Save results
    output_file = "remaining_photos.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'common_name', 'scientific_name', 'source',
            'photo_url', 'original_url', 'attribution', 'license', 'note'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_file}")

    # Print summary with direct Flickr search links for any still missing
    still_missing = [r for r in results if r['source'] == 'NONE']
    if still_missing:
        print(f"\nStill need {len(still_missing)} photos. Manual Flickr search links:")
        for r in still_missing:
            q = r['common_name'].replace(' ', '+')
            print(f"  {r['common_name']}:")
            print(f"    https://www.flickr.com/search/?q={q}&license=2%2C3%2C4%2C5%2C6")


if __name__ == "__main__":
    main()
