"""
Analyze Yelp businesses and export the flattened results to CSV.

Drop into Excel, Google Sheets, Numbers, or import into a database.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/export_to_csv.py > businesses.csv
"""

import csv
import sys

from yelp_analyzer import YelpAnalyzerClient


BUSINESSES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/in-n-out-burger-los-angeles",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
]

COLUMNS = [
    "businessName",
    "rating_normalized",
    "reviewsCount_int",
    "popularity_score",
    "quality_tier",
    "customer_segment",
    "categories",
    "address",
    "neighborhood",
    "phone",
    "website",
    "hours_per_week_total",
    "days_open_count",
    "open_weekends",
    "has_24h_day",
    "is_open_now",
    "online_presence_score",
    "chain_likelihood_score",
    "service_offerings_count",
    "business_listing_age_years",
    "estimated_first_listed_year",
    "website_tech_stack",
    "website_alive",
]


def flatten(rec: dict) -> dict:
    out = {}
    for col in COLUMNS:
        v = rec.get(col)
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        out[col] = v
    return out


def main() -> None:
    client = YelpAnalyzerClient()
    results = client.analyze(BUSINESSES, max_concurrency=3)

    writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    writer.writeheader()
    for r in results:
        if not r.get("success"):
            continue
        writer.writerow(flatten(r))


if __name__ == "__main__":
    main()
