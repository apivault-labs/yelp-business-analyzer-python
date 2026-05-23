# Yelp Business Analyzer — Python SDK

[![PyPI version](https://img.shields.io/badge/pip-yelp--business--analyzer-blue.svg)](https://github.com/apivault-labs/yelp-business-analyzer-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/apivault-labs/yelp-business-analyzer-python/actions/workflows/ci.yml/badge.svg)](https://github.com/apivault-labs/yelp-business-analyzer-python/actions/workflows/ci.yml)

> **40+ enrichment fields per Yelp business. $0.003 each. CRM-ready output.
> One-click outreach links. Sales-ops workflow built-in.**

Direct alternative to **Yelp Fusion API** for use cases the Fusion API can't
cover: tech stack detection, real public emails, social profiles, lead
scoring, industry-specific outreach pitches, and ready-to-paste mailto/SMS/
WhatsApp/LinkedIn-search URLs — none of which the official API exposes.

```bash
pip install git+https://github.com/apivault-labs/yelp-business-analyzer-python
```

```python
from yelp_analyzer import YelpAnalyzerClient

client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")

businesses, summary = client.analyze([
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/diptyque-san-francisco-2",
])

# Top sales prospects, sorted
for b in client.filter_by_lead_tier(businesses, "scorching", "hot"):
    contact = b.get("bestContact") or {}
    print(f"{b['businessName']:30}  lead={b['leadScore']}  {contact.get('value')}")

# One-click outreach
for b in client.filter_with_email(businesses):
    mailto = (b.get("outreachLinks") or {}).get("mailto_url_with_pitch")
    print(mailto)
```

## What you get for $0.003 per business

For every Yelp URL analyzed, you get a single rich JSON record combining
**11 public data sources** + **30+ derived intelligence signals**.

### ⭐ Core (Yelp)
- Business name, rating, review count
- Categories, price range
- Address, phone, website, hours, neighborhood, image, amenities

### 🕐 Hours intelligence
- **Structured weekly schedule** — one entry per day with opens/closes
- **Total hours per week**, days open count
- **Open weekends**, has 24-hour day
- **Real-time `is_open_now`** — **timezone-aware** (PT/MT/CT/ET, ...)

### 🛠️ Website tech stack — 50+ platforms detected
- E-commerce: Shopify, WooCommerce, BigCommerce, Magento, Wix, Squarespace,
  Webflow, Square Online, Weebly, Duda, Ecwid
- Restaurant tech: OpenTable, Resy, Tock, SevenRooms, BentoBox, ChowNow,
  Toast, Olo, Yelp Reservations
- Delivery: DoorDash, Uber Eats, Grubhub, Postmates, Caviar, Slice, ezCater
- Booking: Calendly, Acuity, Mindbody, Vagaro, Booksy, Square Appointments
- Payments: Stripe, PayPal, Square POS, Clover, Lightspeed, Apple Pay,
  Google Pay, Klarna, Affirm, Afterpay
- Marketing: Mailchimp, Klaviyo, Constant Contact, ActiveCampaign, HubSpot
- Analytics: GA, GTM, Facebook Pixel, TikTok Pixel, Hotjar, Microsoft Clarity
- Reviews: Yotpo, Trustpilot, Judge.me
- Chat: Intercom, Zendesk, Drift, Tidio
- Plus **server header**, **HSTS check**, **alive verification**

### 📞 Contact enrichment
- **Real emails** — with CloudFlare email decoder (recovers ~25% of
  obfuscated `data-cfemail` spans on WordPress/Wix sites)
- **Email pattern guesser** — 11 likely contacts for the discovered domain
  (`info@`, `hello@`, `contact@`, `support@`, `sales@`, ...)
- **Phones** in E.164 format with click-to-call URL
- **7 social platforms** detected: Instagram, Facebook, Twitter/X, TikTok,
  YouTube, LinkedIn, Pinterest (extracted from `<a>` tags AND merged from
  JSON-LD `sameAs[]` for higher accuracy)
- **Action links**: menu URL, booking URL, delivery URLs

### 🔍 SEO + mobile-friendliness audit
- `seo_title`, `seo_meta_description`, `seo_canonical`, `seo_og_tags{}`
- `seo_h1_count`, `mobile_has_viewport`, `mobile_has_responsive_css`
- **`seo_hygiene_score`** (0-100)

### 🏷️ Structured amenities — 28 boolean flags
`has_outdoor_seating`, `accepts_reservations`, `offers_delivery`,
`accepts_credit_cards`, `accepts_contactless`, `wifi_available`,
`parking_available`, `wheelchair_accessible`, `good_for_kids`,
`good_for_groups`, `serves_alcohol`, `has_happy_hour`, `vegan_options`,
`vegetarian_options`, `gluten_free_options`, `serves_breakfast`/`brunch`/
`lunch`/`dinner`, `open_late_night`, `dog_friendly`, `has_tvs`,
`live_entertainment`, `private_dining`, `bike_parking`, `has_health_score`

### 🏠 Address parser
`parsedAddress.{street, city, state, zipCode, country, formattedAddress}` +
**`timezone`** derived from US state code (used for the timezone-aware
`is_open_now`).

### 📜 JSON-LD schema.org parsing
When the discovered website publishes Schema.org markup, we extract:
`schema_same_as[]`, `schema_telephones[]`, `schema_emails[]`,
`schema_address`, `schema_latitude/longitude`, `schema_founders[]`,
`schema_legal_name`, `schema_founding_date`.

### ⏱️ Listing & domain age
- Wayback Machine: earliest snapshot of the Yelp page → years on Yelp
- Optional crt.sh SSL history → website domain age (legitimacy signal)

### 🎯 **Lead score 0-100 + best contact + outreach pitch + outreach links**
- **`leadScore`** (0-100) — composite of website health, modern tech stack,
  contact data quality, popularity, SEO hygiene, quality tier, JSON-LD
  legitimacy signals
- **`leadTier`** — `cold` / `warm` / `hot` / `scorching`
- **`leadScoreReasons[]`** — explainable signals
- **`bestContact: {channel, value, label}`** — most actionable handle
  (priority: email > E.164 phone > IG > FB > LinkedIn > website)
- **`outreachPitch`** — ready-to-paste cold-outreach message tailored to the
  Yelp category. **15 industry templates**: restaurants, salons, dentists,
  auto, plumbers/HVAC/electricians, lawyers, real estate, fitness, hotels,
  retail, pet care, events/wedding, cleaning, education, finance.
- **`outreachLinks{}`** — one-click URLs:
  - `mailto_url_with_pitch` (subject + outreach pitch as body)
  - `tel_url`, `sms_url`, `whatsapp_url` (auto-pasted pitch)
  - `linkedin_search_url` — pre-filtered people search
  - `google_search_url`
  - `yelp_competitors_url` — territory research

### 🛡️ Slug-fallback path

When Thunderbit hits a Yelp throttle, the actor doesn't give up — it
reverse-engineers the business name and city from the URL slug
(`tartine-bakery-san-francisco` → `"Tartine Bakery"` + `"San Francisco"`),
then runs the entire **website-discovery → enrichment chain**. Recovers
~60% of previously-failed runs into useful partial records (website + tech
stack + emails + lead score) instead of `success: false`.

## Sample output

```json
{
  "success": true,
  "dataSource": "thunderbit",
  "businessName": "Diptyque Geary Street",
  "rating_normalized": 4.2,
  "reviewsCount_int": 107,
  "categories": "Candle Stores",
  "address": "73 Geary St\nSan Francisco, CA 94108",
  "parsedAddress": {
    "street": "73 Geary St",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94108",
    "country": "US"
  },
  "timezone": "America/Los_Angeles",
  "weekly_schedule": [
    {"day": "Monday", "opens": "10:00", "closes": "18:00"},
    {"day": "Sunday", "opens": "12:00", "closes": "17:00"}
  ],
  "hours_per_week_total": 53,
  "is_open_now": true,
  "website": "https://stores.diptyqueparis.com/en_eu/diptyque-san-francisco",
  "website_discovered_via": "duckduckgo",
  "website_alive": true,
  "website_tech_stack": ["Magento", "Google Analytics"],
  "phones_from_website": ["+14154020600", "415 402 0600"],
  "phoneE164": "+14154020600",
  "social_profiles": {
    "instagram": "https://www.instagram.com/diptyque",
    "facebook": "https://www.facebook.com/diptyque",
    "youtube": "https://www.youtube.com/@DiptyqueParis"
  },
  "seo_title": "Diptyque San Francisco",
  "seo_hygiene_score": 95,
  "mobile_friendly": true,
  "customer_segment": "upscale",
  "quality_tier": "great",
  "popularity_score": 59,
  "online_presence_score": 76,
  "leadScore": 60,
  "leadTier": "hot",
  "leadScoreReasons": [
    "website live", "2 tech detected", "3 social profiles",
    "phone available", "strong SEO hygiene", "great quality"
  ],
  "bestContact": {
    "channel": "instagram",
    "value": "https://www.instagram.com/diptyque"
  },
  "outreachPitch": "Hi Diptyque Geary Street — saw you on Yelp. We help candle stores stores turn local Yelp searches into in-store visits with click-and-collect + reservation messaging. 15 mins to demo?",
  "outreachLinks": {
    "tel_url": "tel:+14154020600",
    "whatsapp_url": "https://wa.me/14154020600?text=...",
    "linkedin_search_url": "https://www.linkedin.com/search/results/people/?keywords=%22Diptyque+Geary+Street%22+owner+OR+founder+OR+CEO",
    "google_search_url": "https://www.google.com/search?q=%22Diptyque+Geary+Street%22+San+Francisco",
    "yelp_competitors_url": "https://www.yelp.com/search?find_desc=Candle+Stores&find_loc=Union+Square"
  }
}
```

## Use cases

### B2B lead generation (the headline use case)
- Filter `leadTier = "scorching"` for warmest prospects
- Filter `website_tech_stack contains "Shopify"` for match-fit leads
- Filter `chain_likelihood_score < 50` to focus on independents
- Use `bestContact` for outreach orchestration
- Use `outreachPitch` as the first cold-email/cold-DM draft
- Use `phoneE164` + `phoneTel` for click-to-call dialers
- Drop the CSV directly into HubSpot / Pipedrive / Salesforce / Apollo

### Niche directory & aggregator building
- "Best date-night restaurants" → `private_dining=true` +
  `serves_alcohol=true` + `priceRange="$$$"`
- "Family-friendly cafés" → `good_for_kids` + `wifi_available` +
  `outdoor_seating`
- "24-hour spots" → `has_24h_day=true`

### Local SEO / tech adoption research
- Track what % of restaurants in a market use Toast / OpenTable / Resy
- Identify SMBs without HSTS / mobile-friendly sites for upsell
- Map `customer_segment` distribution by neighborhood

### CRM enrichment pipeline
- Batch-enrich a list of Yelp URLs and get phones in E.164, validated
  emails, and 7-platform social profiles in a single CSV.

## Pricing

| Volume | Cost |
|---|---|
| 1 business | $0.003 |
| 100 | $0.30 |
| 1,000 | $3.00 |
| 10,000 | $30.00 |

Pay only for what you extract. No subscriptions, no hidden fees, no API
keys to manage. The Apify free tier ($5 credit) covers ~1,500 businesses.

```python
client.estimate_cost(2_500)   # 7.5 USD
```

## Installation

```bash
pip install git+https://github.com/apivault-labs/yelp-business-analyzer-python
```

Or pin to a release tag:
```bash
pip install git+https://github.com/apivault-labs/yelp-business-analyzer-python@v0.2.0
```

## Setup

1. Create an Apify account: <https://console.apify.com/sign-up>
2. Get your API token: <https://console.apify.com/account/integrations>
3. Either pass it explicitly or export `APIFY_API_TOKEN`:

```bash
export APIFY_API_TOKEN="apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

```python
client = YelpAnalyzerClient()                     # picks up env var
client = YelpAnalyzerClient(api_token="apify_...") # explicit
```

## Examples

| File | What it shows |
|---|---|
| [`examples/quickstart.py`](examples/quickstart.py) | Single-business quickstart |
| [`examples/bulk_analyze.py`](examples/bulk_analyze.py) | Multi-business with summary |
| [`examples/lead_scoring_pipeline.py`](examples/lead_scoring_pipeline.py) | Full sales-ops workflow (TOP_LEADS, filters, outreach) |
| [`examples/crm_outreach_links.py`](examples/crm_outreach_links.py) | Paste mailto/whatsapp/linkedin URLs into your CRM |
| [`examples/tech_stack_prospecting.py`](examples/tech_stack_prospecting.py) | Find Shopify/WordPress/OpenTable users |
| [`examples/email_pattern_outreach.py`](examples/email_pattern_outreach.py) | Use guessed emails when no real one is found |
| [`examples/find_chains_vs_indies.py`](examples/find_chains_vs_indies.py) | Independent SMB filter |
| [`examples/open_now_finder.py`](examples/open_now_finder.py) | Timezone-aware open-now |
| [`examples/compare_neighborhoods.py`](examples/compare_neighborhoods.py) | Neighborhood-level distribution |
| [`examples/export_to_csv.py`](examples/export_to_csv.py) | CSV export for CRM import |

## API reference

### `YelpAnalyzerClient(api_token=None, timeout=900, poll_interval=3.0)`

### `analyze(business_urls, **kwargs) -> (businesses, summary)`
Forwards all 18 actor input flags. See the full list in
[`yelp_analyzer/client.py`](yelp_analyzer/client.py).

### `analyze_one(business_url, **kwargs) -> dict`

### `get_summary() -> dict | None`
Aggregate stats for the most recent run.

### `get_top_leads() -> dict | None`
Top 20 prospects (sorted by `leadScore`) with the most-actionable fields
flattened — perfect for Slack-bot alerts or daily sales digests.

### Filters (all return new lists)

- `filter_by_lead_tier(businesses, *tiers)` — `cold` / `warm` / `hot` / `scorching`
- `filter_by_quality(businesses, *tiers)`
- `filter_by_segment(businesses, *segments)` — `budget` / `mid-range` / `upscale` / `luxury`
- `filter_independents(businesses, max_chain_score=25)`
- `filter_with_email(businesses, include_guessed=False)`
- `filter_with_phone(businesses)`
- `filter_open_now(businesses)`
- `filter_by_state(businesses, *states)` — US 2-letter codes
- `filter_by_tech(businesses, *tech_names, match_all=False)`

### `estimate_cost(business_count) -> float`

## How it works

```
your_code → YelpAnalyzerClient → Apify API
                                    ↓
                            Apify actor v1.4
                                    ↓
                  ┌─────────────────┴─────────────────┐
                  ↓                                   ↓
         Thunderbit (Yelp data)              Slug fallback
                  ↓                                   ↓
             ┌────┴────────┬───────┬────────────────┴───┐
             ↓             ↓       ↓                    ↓
       DDG website     JSON-LD    Tech stack       Email/phone
        discovery      schema.org  detector         enrichment
             ↓             ↓       ↓                    ↓
                          rich record
                            ↓
                       you, in Python
```

All heavy lifting (HTTP, retries, parsing, scoring, formatting) happens on
Apify's infrastructure. Your Python process is just an orchestrator —
~150 lines of boilerplate that turn one rich actor into a friendly Pythonic
API surface.

## Why direct Yelp scraping isn't viable from your laptop

Yelp uses **DataDome enterprise WAF**, which blocks all datacenter and most
residential IP ranges with a JS challenge. Solving the challenge requires
a headless browser (~$0.05/run in compute), which would zero out the $3/1K
margin. Thunderbit (used internally by the actor) maintains a whitelisted
pool that can handle the WAF, plus the slug-fallback recovers value when
their pool is throttled. You don't have to think about any of this.

## Keywords

`yelp-scraper` `yelp-api` `yelp-business-analyzer` `yelp-fusion-alternative`
`yelp-without-api-key` `yelp-ratings-api` `yelp-hours-api` `yelp-tech-stack`
`yelp-leads` `yelp-emails` `yelp-phone-numbers` `local-business-intelligence`
`local-lead-generation` `restaurant-analytics` `restaurant-api`
`lead-generation` `b2b-lead-gen` `crm-enrichment` `lead-score`
`outreach-automation` `cold-email` `sales-intelligence` `sales-ops`
`is-open-now-api` `chain-detection` `popularity-score`
`hubspot-alternative` `apollo-alternative` `hunter-alternative`
`web-scraping` `apify` `python-sdk`

## License

MIT — see [LICENSE](LICENSE).
