"""
Analyze many Yelp businesses in one batch.

The actor itself runs them in parallel on Apify infrastructure, so a single
``analyze`` call with many URLs is faster and cheaper than calling the SDK
once per business.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_analyze.py
"""

from yelp_analyzer import YelpAnalyzerClient


BUSINESSES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/in-n-out-burger-los-angeles",
    "https://www.yelp.com/biz/joes-pizza-new-york-2",
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",
]


def main() -> None:
    client = YelpAnalyzerClient(timeout=900)
    print(f"Analyzing {len(BUSINESSES)} businesses "
          f"(estimated cost: ${client.estimate_cost(len(BUSINESSES))})...\n")

    results = client.analyze(
        BUSINESSES,
        max_concurrency=3,
        # speed-ups: skip slower data sources if you don't need them
        extract_age=True,         # Wayback — slowest
        extract_website=True,
    )

    print(f"{'Name':<30} {'Rating':>7} {'Reviews':>8} {'Pop':>4} {'Quality':>12}")
    print("-" * 70)
    for r in sorted(results, key=lambda x: -(x.get("popularity_score") or 0)):
        if not r.get("success"):
            print(f"  ERROR: {r.get('inputUrl')}: {r.get('error', '?')}")
            continue
        name = (r.get("businessName") or "(unknown)")[:30]
        rating = r.get("rating_normalized") or "?"
        reviews = r.get("reviewsCount_int") or 0
        pop = r.get("popularity_score") or "?"
        quality = r.get("quality_tier", "?")[:12]
        print(f"{name:<30} {str(rating):>7} {reviews:>8,} {str(pop):>4} {quality:>12}")


if __name__ == "__main__":
    main()
