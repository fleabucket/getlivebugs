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

echo "Step 3/3: Matching species to products..."
echo ""
python3 match_species.py
