# Yelp Business Analyzer — Python SDK

> **Real-time Yelp business intelligence: ratings, structured hours, website tech stack, listing age, popularity score & chain detection — all in one API call.**

Python client for the [Yelp Business Analyzer Apify Actor](https://apify.com/apivault_labs/yelp-business-scraper) — get **15+ business intelligence signals** for any Yelp business page using only public data sources.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/yelp-business-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyPI-friendly](https://img.shields.io/badge/install-pip-success)](#installation)

---

## What it does

For any Yelp business URL, this actor returns a single rich JSON record combining **4 public data sources** + **15+ derived intelligence signals**.

A direct, pay-per-use alternative to:
- [Yelp Fusion API](https://www.yelp.com/developers) (rate-limited, requires app review, no hours intelligence)
- Manual Yelp scraping (anti-bot, fragile)
- Generic local-business APIs

**Pricing:** $0.003 per business analyzed. No subscriptions, no credits expiring, no rate limits.

---

## Quick start

```python
from yelp_analyzer import YelpAnalyzerClient

client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")

result = client.analyze_one("https://www.yelp.com/biz/tartine-bakery-san-francisco")

print(f"Name:           {result['businessName']}")
print(f"Rating:         {result['rating']}⭐ × {result['reviewsCount']} reviews")
print(f"Quality:        {result['quality_tier']}")
print(f"Popularity:     {result['popularity_score']}/100")
print(f"Hours/week:     {result['hours_per_week_total']}")
print(f"Open weekends:  {result['open_weekends']}")
print(f"Open right now: {result['is_open_now']}")
```

Output:
```
Name:           Tartine Bakery
Rating:         4.2⭐ × 9200 reviews
Quality:        great
Popularity:     84/100
Hours/week:     73.5
Open weekends:  True
Open right now: False
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/yelp-business-analyzer-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/yelp-business-analyzer-python.git
cd yelp-business-analyzer-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")
```

---

## What you get for $0.003 per business

### ⭐ Core fields (real-time, no cache)
- Business name, rating, review count
- Categories, price range
- Full address with neighborhood
- Phone, website
- Free-text business hours
- Profile image and amenities

### 🕐 Hours Intelligence
- **Structured weekly schedule** — `[{day, opens, closes}, ...]`
- **Total hours per week**
- **Days open count** (1-7)
- **Open weekends** boolean
- **Has 24-hour day** boolean
- **Real-time `is_open_now`** check (UTC-aware)

### 🛠️ Website Tech Stack (when business has external site)
Detect 20+ platforms a small business might use:
- **E-commerce:** Shopify, WooCommerce, BigCommerce, Magento, Wix, Squarespace, Webflow, Square Online
- **Restaurant tools:** OpenTable, Resy, Toast, ChowNow, Bento, Olo
- **Generic:** WordPress, GoDaddy
- **Marketing:** Mailchimp, Klaviyo, Google Analytics, Facebook Pixel
- **Server header**, **HSTS** flag, **alive check**, **website emails**

### ⏱️ Business Listing Age
- Earliest Wayback Machine snapshot of the Yelp page
- **Estimated business listing age in years**
- **First listed year** on Yelp

### 🧠 Derived Intelligence (8 signals)
- **`popularity_score`** (0-100) — composite of rating × log(reviews)
- **`customer_segment`** — budget / mid-range / upscale / luxury (by $-tier)
- **`quality_tier`** — poor / fair / good / great / exceptional
- **`online_presence_score`** (0-100) — has website, tech stack, contact, amenities
- **`chain_likelihood_score`** (0-100) — franchise / chain detection heuristic
- **`service_offerings_count`** — amenities + categories
- **`rating_normalized`**, **`reviewsCount_int`** — typed numeric fields for sorting

---

## Examples

See the [`examples/`](examples) folder for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Analyze one business, print key metrics |
| [`bulk_analyze.py`](examples/bulk_analyze.py) | Analyze 50+ businesses in parallel |
| [`find_chains_vs_indies.py`](examples/find_chains_vs_indies.py) | Filter chains from independent businesses |
| [`export_to_csv.py`](examples/export_to_csv.py) | Save results to CSV / Excel |
| [`compare_neighborhoods.py`](examples/compare_neighborhoods.py) | Compare quality / pricing across neighborhoods |
| [`open_now_finder.py`](examples/open_now_finder.py) | Filter businesses currently open right now |

---

## API reference

### `YelpAnalyzerClient(api_token=None, timeout=600)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for analysis. Default 600 (10 min). |

### `client.analyze(business_urls, **kwargs)`

Analyze multiple businesses synchronously.

| Param | Type | Default | Description |
|---|---|---|---|
| `business_urls` | `list[str]` | required | Yelp business URLs (`yelp.com/biz/...`) |
| `max_concurrency` | `int` | 2 | Parallel businesses to analyze |
| `actor_timeout_secs` | `int` | 300 | Max actor runtime (passed to Apify) |

Plus boolean toggles to skip data sources for speed:

| Flag | Default | Effect |
|---|---|---|
| `extract_core` | `True` | Thunderbit core fields (name, rating, hours, ...) |
| `extract_hours_intel` | `True` | Structured weekly schedule + is-open-now |
| `extract_website` | `True` | Detect tech stack on business website |
| `extract_age` | `True` | Wayback listing age |
| `extract_derived_signals` | `True` | popularity, segment, quality, chain detection |

Returns: `list[dict]` — one record per business.

### `client.analyze_one(business_url, **kwargs)`

Convenience wrapper for single-business analysis. Returns one `dict`.

### `client.estimate_cost(business_count)`

Returns the estimated USD cost (`business_count × 0.003`).

---

## Sample output

```json
{
  "success": true,
  "inputUrl": "https://www.yelp.com/biz/tartine-bakery-san-francisco",
  "businessName": "Tartine Bakery",
  "rating": "4.2",
  "rating_normalized": 4.2,
  "reviewsCount": "9200",
  "reviewsCount_int": 9200,
  "categories": "Bakeries, Cafes, Desserts",
  "address": "600 Guerrero St, San Francisco, CA 94110",
  "neighborhood": "Mission",
  "amenities": "Claimed; Offers delivery; Takes reservations; Outdoor seating",
  "image": "https://s3-media0.fl.yelpcdn.com/buphoto/...jpg",
  "hours": "Mon-Sun: 7:30 AM - 6:00 PM",
  "weekly_schedule": [
    {"day": "Monday",   "opens": "07:30", "closes": "18:00"},
    {"day": "Tuesday",  "opens": "07:30", "closes": "18:00"}
  ],
  "hours_per_week_total": 73.5,
  "days_open_count": 7,
  "open_weekends": true,
  "has_24h_day": false,
  "is_open_now": false,
  "customer_segment": "unknown",
  "quality_tier": "great",
  "popularity_score": 84,
  "online_presence_score": 30,
  "chain_likelihood_score": 5,
  "service_offerings_count": 13
}
```

---

## Use cases

### 🥇 Local Lead Generation
Find prospects with **website tech stack** matching your tool:
- Shopify users → pitch e-commerce apps
- WordPress users → pitch plugins/hosting
- Stores **without** Klaviyo → pitch email automation
- Restaurants without Toast/Resy → pitch reservation systems

### 🥈 Directory & Aggregator Building
Build verified business directories with:
- Confirmed listing age for "established" badges
- Real opening hours per weekday
- Real category and price tier data
- Confirmed website status (alive vs broken)

### 🥉 Competitive Research
- Benchmark `popularity_score` across competitors
- Track `online_presence_score` over time
- Identify chains in a market via `chain_likelihood_score`
- Analyze customer segment distribution by neighborhood

### 🍽️ Restaurant / Hospitality Analytics
- Find late-night spots (`has_24h_day`, `hours_per_week_total`)
- Identify weekend brunch markets (`open_weekends`)
- Detect modern POS adoption (Toast, Square, OpenTable)
- Filter restaurants by `quality_tier` for editorial picks

### 📊 Investment & M&A Due Diligence
- Verify business legitimacy via `business_listing_age_years`
- Check `quality_tier` consistency
- Cross-reference review patterns for chain vs indie

### 🗺️ Real-time "Open Now" Apps
- Use `is_open_now` for currently-open business filters
- Combine with `weekly_schedule` for "open in 30 minutes" features
- Power dynamic local search interfaces

---

## Pricing

Pay only for what you analyze:

| Volume | Cost |
|---|---|
| 1 business | $0.003 |
| 100 businesses | $0.30 |
| 1,000 businesses | $3.00 |
| 10,000 businesses | $30.00 |

Free Apify tier includes ~$5 monthly credit — analyze ~1,500 businesses per month for free.

---

## How it works

All data comes from **public sources** — no logins, no Yelp accounts, no proxies needed:

1. **Thunderbit AI scraper** — extracts the 12 core Yelp fields (name, rating, hours, ...)
2. **Hours parser** — turns Thunderbit's free-text hours into a structured weekly schedule
3. **Website fetcher** — quick HEAD + GET to detect tech stack and verify the site is alive
4. **Wayback Machine** — `archive.org/wayback/available` for first snapshot date
5. **Real-time clock** — UTC-aware `is_open_now` calculation against the parsed schedule

Popularity score formula:
```
popularity_score = (rating_normalized × 50) + (log10(reviews) × 12.5)
clamped to [0, 100]
```
Designed so 4.5★ × 1000 reviews ≈ 85, 5.0★ × 5 reviews ≈ 25.

---

## Speed & reliability

- **15–25 seconds per business** (parallel HTTP, no rendering)
- **2 businesses in parallel** by default (Yelp-friendly, configurable up to 5)
- **No proxies needed** — Thunderbit handles Yelp scraping for us
- **Graceful degradation** — if Wayback is slow or a website is down, other layers still return data

---

## FAQ

**Q: Do I need a Yelp Fusion API key?**
A: No. This actor uses public Yelp pages, not the Fusion API. No app review, no rate limits, no quota.

**Q: How fresh is the data?**
A: 100% real-time. No caching. Each call hits Yelp's live page.

**Q: Will it work on every Yelp listing?**
A: Yes — every public business page (`yelp.com/biz/...`).

**Q: Why is `popularity_score` not just rating?**
A: A 5★ business with 3 reviews isn't actually popular. We combine rating with log-scaled review count so 4.5★ × 1000 reviews ≈ 85, while 5.0★ × 5 reviews ≈ 25. Better signal for ranking.

**Q: How accurate is `chain_likelihood_score`?**
A: It's a heuristic combining brand-name matching and review patterns. Scores 50+ almost always indicate chains. Under 25 = independent business.

**Q: Can it scrape Yelp reviews?**
A: Not in this client — see the companion **[Yelp Reviews Scraper](https://apify.com/apivault_labs/yelp-reviews-scraper)** for full review extraction with reviewer info.

**Q: Can I run this without Apify?**
A: This package is a thin wrapper around the hosted actor. The actor handles infrastructure, retries, parallelism. Self-hosted Yelp scraping at scale requires anti-bot mitigation and proxies — generally not worth building yourself.

---

## Related Apify actors

- [Yelp Reviews Scraper](https://apify.com/apivault_labs/yelp-reviews-scraper) — full reviews with text and reviewer info
- [Local Lead Finder](https://apify.com/apivault_labs/local-business-lead-finder) — find businesses without websites
- [Trustpilot Reviews Scraper](https://apify.com/apivault_labs/trustpilot-reviews-scraper) — review intelligence for any brand
- [Domain Intelligence Scraper](https://apify.com/apivault_labs/domain-intelligence-scraper) — WHOIS, DNS, SSL for any domain

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.003/business).

---

## Keywords

`yelp-scraper` `yelp-api` `yelp-business-analyzer` `yelp-business-api` `yelp-ratings-api` `yelp-reviews-api` `yelp-hours-api` `yelp-tech-stack` `yelp-fusion-alternative` `local-business-intelligence` `local-lead-generation` `restaurant-analytics` `restaurant-api` `business-hours-api` `is-open-now-api` `chain-detection` `popularity-score` `web-scraping` `apify` `apify-actor` `python-sdk` `yelp-without-api-key` `yelp-no-key` `business-listing-scraper` `yelp-popularity-score`
