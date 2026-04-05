"""
GetLiveBugs.com — Photo Collector for New Species Batch
========================================================
Pulls CC-licensed photos from iNaturalist and Wikipedia for 32 new species.

HOW TO RUN:
1. Place this file and new_species_photos_input.csv in the same folder
2. pip3 install requests
3. python3 collect_new_photos.py
4. Output: new_species_photos.csv (mapping of species to photo URLs + licenses)
"""

import requests
import csv
import time
import os

HEADERS = {
    'User-Agent': 'GetLiveBugs/1.0 (getlivebugs.com; collecting CC-licensed species photos)',
}


def search_inaturalist(scientific_name):
    """Search iNaturalist for research-grade photos."""
    try:
        # Find taxon ID
        response = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={'q': scientific_name, 'rank': 'species', 'per_page': 3},
            headers=HEADERS,
            timeout=10
        )
        data = response.json()

        if not data.get('results'):
            # Try without subspecies/morph info
            base_name = scientific_name.split("'")[0].split('"')[0].strip()
            if base_name != scientific_name:
                response = requests.get(
                    "https://api.inaturalist.org/v1/taxa",
                    params={'q': base_name, 'rank': 'species', 'per_page': 3},
                    headers=HEADERS,
                    timeout=10
                )
                data = response.json()
            if not data.get('results'):
                return None

        taxon = data['results'][0]
        taxon_id = taxon['id']

        # Check default photo
        default_photo = taxon.get('default_photo', {})
        if default_photo:
            license_code = default_photo.get('license_code', '')
            if license_code and license_code.lower() in ['cc-by', 'cc-by-sa', 'cc0']:
                return {
                    'source': 'iNaturalist',
                    'photo_url': default_photo.get('medium_url', '').replace('medium', 'large'),
                    'original_url': default_photo.get('original_url', default_photo.get('medium_url', '').replace('medium', 'original')),
                    'attribution': default_photo.get('attribution', ''),
                    'license': license_code,
                    'inaturalist_taxon_id': taxon_id,
                }

        # Search observations for CC photo
        time.sleep(0.5)
        obs_response = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params={
                'taxon_id': taxon_id,
                'quality_grade': 'research',
                'photos': 'true',
                'per_page': 5,
                'order_by': 'votes',
                'photo_license': 'cc-by,cc-by-sa,cc0',
            },
            headers=HEADERS,
            timeout=10
        )
        obs_data = obs_response.json()

        for obs in obs_data.get('results', []):
            for photo in obs.get('photos', []):
                license_code = photo.get('license_code', '')
                if license_code and license_code.lower() in ['cc-by', 'cc-by-sa', 'cc0']:
                    return {
                        'source': 'iNaturalist',
                        'photo_url': photo.get('url', '').replace('square', 'large'),
                        'original_url': photo.get('url', '').replace('square', 'original'),
                        'attribution': photo.get('attribution', ''),
                        'license': license_code,
                        'inaturalist_taxon_id': taxon_id,
                    }
    except Exception as e:
        print(f"    iNaturalist error: {e}")
    return None


def search_wikipedia(scientific_name):
    """Search Wikipedia for a photo."""
    try:
        clean_name = scientific_name.split("'")[0].split('"')[0].strip()
        response = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + clean_name.replace(' ', '_'),
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            original_image = data.get('originalimage', {})
            thumbnail = data.get('thumbnail', {})
            if original_image:
                return {
                    'source': 'Wikimedia Commons',
                    'photo_url': thumbnail.get('source', ''),
                    'original_url': original_image.get('source', ''),
                    'attribution': 'See Wikimedia Commons for attribution',
                    'license': 'Check individual image license',
                    'inaturalist_taxon_id': '',
                }
    except Exception as e:
        print(f"    Wikipedia error: {e}")
    return None


def main():
    input_file = "new_species_photos_input.csv"
    if not os.path.exists(input_file):
        print(f"ERROR: {input_file} not found. Place it in the same folder as this script.")
        return

    species_list = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            species_list.append(row)

    print(f"GetLiveBugs.com — Photo Collector (New Species Batch)")
    print(f"=" * 55)
    print(f"Processing {len(species_list)} species...\n")

    results = []
    found = 0
    not_found_list = []

    for i, species in enumerate(species_list):
        sci_name = species['scientific_name']
        common_name = species['common_name']

        print(f"[{i+1}/{len(species_list)}] {common_name} ({sci_name})")

        # Try iNaturalist first
        photo = search_inaturalist(sci_name)

        # Fallback to Wikipedia
        if not photo:
            time.sleep(0.5)
            photo = search_wikipedia(sci_name)

        if photo:
            photo['scientific_name'] = sci_name
            photo['common_name'] = common_name
            photo['category'] = species.get('category', '')
            results.append(photo)
            found += 1
            print(f"  ✓ Found from {photo['source']} ({photo['license']})")
        else:
            results.append({
                'scientific_name': sci_name,
                'common_name': common_name,
                'category': species.get('category', ''),
                'source': 'NONE',
                'photo_url': '',
                'original_url': '',
                'attribution': '',
                'license': '',
                'inaturalist_taxon_id': '',
            })
            not_found_list.append(common_name)
            print(f"  ✗ No photo found — will need manual sourcing")

        time.sleep(1.5)

    # Write results
    output_file = "new_species_photos.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'scientific_name', 'common_name', 'category',
            'source', 'photo_url', 'original_url',
            'attribution', 'license', 'inaturalist_taxon_id'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n{'=' * 55}")
    print(f"Results saved to {output_file}")
    print(f"Photos found: {found}/{len(species_list)}")

    if not_found_list:
        print(f"\nNEED MANUAL PHOTOS ({len(not_found_list)}):")
        for name in not_found_list:
            print(f"  - {name}")
        print(f"\nFor these, check breeder product photos or search")
        print(f"Flickr/Instagram for CC-licensed images of these morphs.")


if __name__ == "__main__":
    main()
