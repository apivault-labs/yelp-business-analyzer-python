"""
Analyze Yelp businesses and export the flattened results to CSV.

Two ways to do this:

1. Server-side: pass `export_format="csv"` to ``analyze`` — the actor
   returns rows already shaped for CRM import (30 columns flattened).
2. Client-side: keep the rich JSON and write only the columns you care
   about.

Both are shown below.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > businesses.csv
"""

import csv
import sys

from yelp_analyzer import YelpAnalyzerClient


BUSINESSES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
]


def main_server_side_csv() -> None:
    """Recommended: actor flattens to CRM-ready CSV automatically."""
    client = YelpAnalyzerClient()
    rows, _ = client.analyze(BUSINESSES, max_concurrency=3, export_format="csv")
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


COLUMNS_CLIENT_SIDE = [
    "businessName",
    "rating_normalized",
    "reviewsCount_int",
    "popularity_score",
    "leadScore",
    "leadTier",
    "quality_tier",
    "customer_segment",
    "categories",
    "address",
    "city",
    "state",
    "zipCode",
    "neighborhood",
    "phone",
    "phoneE164",
    "primary_email",
    "instagram",
    "facebook",
    "linkedin",
    "website",
    "website_domain",
    "tech_stack_summary",
    "is_open_now",
    "outreach_pitch",
    "mailto_url",
    "linkedin_search_url",
]


def flatten_client_side(rec: dict) -> dict:
    parsed = rec.get("parsedAddress") or {}
    socials = rec.get("social_profiles") or {}
    emails = rec.get("emails_from_website") or rec.get("schema_emails") or []
    tech = rec.get("website_tech_stack") or []
    links = rec.get("outreachLinks") or {}
    return {
        "businessName": rec.get("businessName"),
        "rating_normalized": rec.get("rating_normalized"),
        "reviewsCount_int": rec.get("reviewsCount_int"),
        "popularity_score": rec.get("popularity_score"),
        "leadScore": rec.get("leadScore"),
        "leadTier": rec.get("leadTier"),
        "quality_tier": rec.get("quality_tier"),
        "customer_segment": rec.get("customer_segment"),
        "categories": rec.get("categories"),
        "address": rec.get("address"),
        "city": parsed.get("city"),
        "state": parsed.get("state"),
        "zipCode": parsed.get("zipCode"),
        "neighborhood": rec.get("neighborhood"),
        "phone": rec.get("phone"),
        "phoneE164": rec.get("phoneE164"),
        "primary_email": emails[0] if emails else None,
        "instagram": socials.get("instagram"),
        "facebook": socials.get("facebook"),
        "linkedin": socials.get("linkedin"),
        "website": rec.get("website"),
        "website_domain": rec.get("website_domain"),
        "tech_stack_summary": ", ".join(tech[:5]) if tech else None,
        "is_open_now": rec.get("is_open_now"),
        "outreach_pitch": rec.get("outreachPitch"),
        "mailto_url": (links.get("mailto_url_with_pitch")
                       or links.get("mailto_url")),
        "linkedin_search_url": links.get("linkedin_search_url"),
    }


def main() -> None:
    """Default: client-side flattening (more control over column shape)."""
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(BUSINESSES, max_concurrency=3)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS_CLIENT_SIDE)
    writer.writeheader()
    for r in businesses:
        if not r.get("success"):
            continue
        writer.writerow(flatten_client_side(r))


if __name__ == "__main__":
    main()
