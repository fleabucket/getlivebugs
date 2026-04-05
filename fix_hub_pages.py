"""Fix hub index pages — replace hardcoded mantis references."""
import os

PAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "pages")

CATEGORIES = {
    "isopod": {"name": "Isopod", "title": "Isopods", "desc": "Browse {n} isopod species available from verified US breeders. From the trending Rubber Ducky isopod to beginner-friendly Dairy Cow isopods, find the perfect species for your collection."},
    "jumping-spider": {"name": "Jumping Spider", "title": "Jumping spiders", "desc": "Browse {n} jumping spider species available from verified US breeders. From the beloved Regal jumping spider to the tiny Tan jumping spider, find your perfect pet spider."},
    "millipede": {"name": "Millipede", "title": "Millipede species", "desc": "Browse {n} millipede species available from verified US breeders. From the impressive Giant African millipede to the colorful Bumblebee millipede, find the perfect species."},
    "centipede": {"name": "Centipede", "title": "Centipede species", "desc": "Browse {n} centipede species available from verified US breeders. Impressive display animals for experienced keepers."},
    "beetle": {"name": "Beetle", "title": "Beetle species", "desc": "Browse {n} beetle species available from verified US breeders. From the iconic Blue Death Feigning beetle to the impressive Eastern Hercules beetle."},
    "roach": {"name": "Roach", "title": "Pet roach species", "desc": "Browse {n} pet roach species available from verified US breeders. From the classic Madagascar Hissing cockroach to the stunning Domino roach."},
    "stick-insect": {"name": "Stick Insect", "title": "Stick insect species", "desc": "Browse {n} stick insect and leaf insect species available from verified US breeders. Masters of camouflage and fascinating pets."},
    "moth": {"name": "Moth", "title": "Moth species", "desc": "Browse {n} moth species available from verified US breeders. Raise spectacular moths from cocoons and witness their incredible lifecycle."},
}

for slug, info in CATEGORIES.items():
    index_path = os.path.join(PAGES, slug, "index.astro")
    if not os.path.exists(index_path):
        print(f"  Skipping {slug}/ — no index.astro")
        continue
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Replace the hardcoded mantis references
    content = content.replace("const categorySlug = 'mantis'", f"const categorySlug = '{slug}'")
    content = content.replace("const categoryName = 'Praying Mantis'", f"const categoryName = '{info['name']}'")
    content = content.replace("Buy Praying Mantis", f"Buy {info['name']}s")
    content = content.replace("praying mantis species", info['title'].lower())
    content = content.replace("Praying mantis species", info['title'])
    content = content.replace("Praying Mantis", info['name'])
    content = content.replace("mantis species", f"{info['name'].lower()} species")
    content = content.replace("orchid mantis", info['title'].lower())
    content = content.replace("ghost mantis", info['title'].lower())
    content = content.replace("giant Asian mantis", info['title'].lower())
    
    # Fix the description paragraph
    old_desc = "From the stunning orchid mantis to the beginner-friendly giant Asian mantis,\n      find the perfect species for your experience level and budget."
    # Just replace with a generic one if the old text is still there
    if "stunning" in content and "Asian" in content:
        content = content.replace(
            "From the stunning orchid mantis to the beginner-friendly giant Asian mantis,\n      find the perfect species for your experience level and budget.",
            "Find the perfect species for your experience level and budget."
        )
    
    with open(index_path, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Fixed: {slug}/index.astro")

print("\nDone. Run: npm run build")
