"""
Yelp Business Analyzer — Python SDK

Official Python client for the apivault_labs/yelp-business-scraper Apify
actor (v1.4). Real-time business intelligence for any Yelp business —
40+ enrichment fields per business, sales-ops-ready output, one-click
outreach links, all for $0.003 per business.

Returns per business:

- Core (Yelp): name, rating, reviews, price range, categories, address,
  phone, website, hours, neighborhood, image, amenities
- Hours: structured weekly schedule, hours/week, days open count, weekend
  coverage, 24h-day flag, **timezone-aware is_open_now**
- Website tech stack: 50+ platforms detected (Shopify, Toast, OpenTable,
  Tock, SevenRooms, DoorDash, Uber Eats, Grubhub, Stripe, Square, Klaviyo,
  HubSpot, Yotpo, Intercom, Zendesk, ...)
- Contact enrichment: emails (with CloudFlare decoder), phones (E.164),
  social profiles (IG, FB, TikTok, YouTube, LinkedIn, Pinterest from
  JSON-LD sameAs[])
- JSON-LD: schema.org telephone, email, postal address, geo, founders,
  legal name, founding date
- Email pattern guesser: 11 likely contact addresses for the discovered
  domain (info@, hello@, contact@, ...)
- SEO + mobile audit: title, meta, OG tags, viewport, h1 count, hygiene score
- Action links: menu, booking (OpenTable/Resy/Tock/Calendly), delivery URLs
- Amenities: 28 boolean flags (has_outdoor_seating, accepts_reservations,
  vegan_options, dog_friendly, ...)
- Address parser: street, city, state, zipCode, country + IANA timezone
- Wayback listing age, optional crt.sh domain age
- Derived: popularity_score, customer_segment, quality_tier,
  online_presence_score, chain_likelihood_score
- **leadScore (0-100)** + tier (cold/warm/hot/scorching) + reasons
- bestContact: most actionable handle (email > E.164 phone > IG > FB > ...)
- **outreachPitch**: industry-specific cold-outreach (15 industries)
- **outreachLinks**: one-click mailto/tel/sms/WhatsApp/LinkedIn-search/
  Google-search/Yelp-competitors URLs
- Slug fallback: when Yelp throttles Thunderbit, the actor still recovers
  business name + city from the URL slug and runs all website-based
  enrichment — giving you usable leads instead of `success: false`

Quick start:

    from yelp_analyzer import YelpAnalyzerClient

    client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")

    businesses, summary = client.analyze([
        "https://www.yelp.com/biz/zuni-cafe-san-francisco",
        "https://www.yelp.com/biz/diptyque-san-francisco-2",
    ])

    for b in client.filter_by_lead_tier(businesses, "hot", "scorching"):
        contact = b.get("bestContact") or {}
        print(f"{b['businessName']:30}  {b['leadScore']}  {contact.get('value')}")

    # One-click outreach
    for b in client.filter_with_email(businesses):
        mailto = (b.get("outreachLinks") or {}).get("mailto_url_with_pitch")
        print(mailto)

See https://github.com/apivault-labs/yelp-business-analyzer-python for full docs.
"""

from .client import YelpAnalyzerClient
from .exceptions import (
    YelpAnalyzerError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.2.0"
__all__ = [
    "YelpAnalyzerClient",
    "YelpAnalyzerError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
