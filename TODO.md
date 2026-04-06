# GetLiveBugs.com — TODO
## Updated: April 5, 2026

### Target: 200 suppliers · 400 species · 1,000 pages

---

## NOW (this week)

- [ ] Submit key URLs to Google Search Console — isopod, jumping-spider, beetle, roach, stick-insect, moth hubs + high-value species pages
- [ ] Join Awin affiliate programs — Worm Nerd, Bee Inspired, Best Bee Brothers, Wondercide, Premo Guard, AgroThrive

## NEXT (this month)

- [ ] Species expansion batch 2 — prioritize ants, butterflies, beneficial insects (scraper data already flowing, no pages to show it)
- [ ] Species expansion batch 3 — remaining 321-species backlog toward 400 total
- [ ] Build HTML scrapers for big 5 non-Shopify suppliers (Backwater Reptiles, LLL Reptile, ABDragons, Stateside Ants, Springtails US)
- [ ] Etsy directory links — 12 sellers, manual curation (link + description, no pricing)
- [ ] Isopod morph photos — Rubber Ducky and Magic Potion still show base species. Supplier outreach or Flickr CC search.
- [ ] Fix GitHub Actions Node.js 20 deprecation — hard deadline June 2, 2026. Update actions/checkout and actions/setup-python or add FORCE_JAVASCRIPT_ACTIONS_TO_NODE24 env var.

## LATER (next month+)

- [ ] Google Merchant Center — structured product data (schema.org) for free Shopping listings. Generate feed from scraper inventory.
- [ ] Supplier outreach / Verified Seller badges — email template drafted. Target small ops for photos, backlinks, standardized data.
- [ ] Price history trend charts — data logging in price_history.csv every run. Build display after 4-6 weeks of data.
- [ ] Search feature — client-side species filter for homepage/nav
- [ ] Comparison pages — /compare/italian-vs-carniolan-bees/, etc.
- [ ] Use-case guides — /guides/best-insects-for-garden-pest-control/, etc.
- [ ] Supplier profile pages — /suppliers/fear-not-tarantulas/, future paid listings ($15-30/mo)

## PARKING LOT

- [ ] Email notifications for out-of-stock (Cloudflare Workers + KV)
- [ ] Etsy API or Awin product feed integration (replaces manual links)
- [ ] Direct breeder affiliate deals
- [ ] Paid Featured Seller listings
- [ ] WooCommerce HTML fallback for Clearwater Butterfly + Roach Crossing (API blocked)

---

## COMPLETED (this session — April 5, 2026)

- [x] Suppliers: 38 → 61 (53 Shopify + 8 WooCommerce)
- [x] Removed 5 dead suppliers (Jamie's Tarantulas, The Bug Company, Northwest Beneficials, The Squirm Firm, Rainbow Mealworms)
- [x] Confirmed Shady Oak Butterfly Farm dead
- [x] GitHub Actions workflow fixed — permissions + rebase
- [x] Scraper running successfully, twice-weekly schedule (Sun + Wed)
- [x] WooCommerce Store API scraper built into pipeline (6 of 8 returning data)
- [x] False match filter — 3-layer defense (blocked keys, word boundaries, expanded exclude list)
- [x] Listing enrichment — size (38%), life stage (7%), sex (4%), temperament (5%), per-unit pricing (13%)
- [x] Dynamic meta — homepage body + SEO description pull real counts
- [x] Pricing timestamps — "Prices checked" and "Next update" on for-sale pages
- [x] Amazon Associates applied
- [x] Verified 49 supplier websites, catalogued 12 Etsy-only sellers
- [x] Identified 7 new suppliers from additional research (Springtails US, Terrarium Tribe, ABDragons, Dubi Deli, TopFlight Dubia, NEHERP, Stella's Springtails)
