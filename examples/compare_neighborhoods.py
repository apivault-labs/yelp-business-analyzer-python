"""
Compare the quality, pricing and popularity distribution across two
neighborhoods or cities.

Useful for:
- Real estate research (local amenity density and quality)
- Restaurant group expansion ("which neighborhood has weak competition?")
- Travel guides ("Mission vs Marina foodie scene")

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/compare_neighborhoods.py
"""

from collections import defaultdict

from yelp_analyzer import YelpAnalyzerClient


# Two sets of representative businesses to compare.
# In real use you would pull these from a Yelp search by neighborhood.
GROUP_A = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",       # Mission
    "https://www.yelp.com/biz/foreign-cinema-san-francisco",       # Mission
    "https://www.yelp.com/biz/lazy-bear-san-francisco-2",          # Mission
]
GROUP_B = [
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",    # Yountville
    "https://www.yelp.com/biz/bouchon-yountville",                 # Yountville
    "https://www.yelp.com/biz/ad-hoc-yountville",                  # Yountville
]


def stats(records: list[dict]) -> dict:
    ok = [r for r in records if r.get("success")]
    if not ok:
        return {}
    avg = lambda key: sum(r.get(key) or 0 for r in ok) / len(ok)
    pop = [r.get("popularity_score") or 0 for r in ok]
    return {
        "count": len(ok),
        "avg_rating": round(avg("rating_normalized"), 2),
        "avg_reviews": int(avg("reviewsCount_int")),
        "avg_popularity": round(avg("popularity_score"), 1),
        "avg_online_presence": round(avg("online_presence_score"), 1),
        "max_pop": max(pop) if pop else 0,
        "tiers": {
            t: sum(1 for r in ok if r.get("quality_tier") == t)
            for t in ("exceptional", "great", "good", "fair", "poor")
        },
    }


def main() -> None:
    client = YelpAnalyzerClient()
    a = client.analyze(GROUP_A, max_concurrency=3)
    b = client.analyze(GROUP_B, max_concurrency=3)

    sa = stats(a)
    sb = stats(b)

    rows = [
        ("Count",                "count"),
        ("Avg rating",           "avg_rating"),
        ("Avg reviews",          "avg_reviews"),
        ("Avg popularity",       "avg_popularity"),
        ("Avg online presence",  "avg_online_presence"),
        ("Max popularity",       "max_pop"),
    ]

    print(f"{'Metric':<22} {'Group A':>12} {'Group B':>12}")
    print("-" * 50)
    for label, key in rows:
        print(f"{label:<22} {str(sa.get(key, '-')):>12} {str(sb.get(key, '-')):>12}")

    print("\nQuality tier distribution:")
    for tier in ("exceptional", "great", "good", "fair", "poor"):
        print(f"  {tier:<14} A={sa.get('tiers', {}).get(tier, 0):<3} "
              f"B={sb.get('tiers', {}).get(tier, 0):<3}")


if __name__ == "__main__":
    main()
