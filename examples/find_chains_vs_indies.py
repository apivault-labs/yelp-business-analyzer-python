"""
Filter chain restaurants from independent businesses.

Useful for:
- Editorial coverage (skip chains for "best independent restaurants" lists)
- Lead generation (target indies for boutique products)
- Investment research (chains have different ops than indies)
- Local market analysis (chain density per neighborhood)

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/find_chains_vs_indies.py
"""

from yelp_analyzer import YelpAnalyzerClient


CANDIDATES = [
    "https://www.yelp.com/biz/starbucks-san-francisco-100",
    "https://www.yelp.com/biz/in-n-out-burger-los-angeles",
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",
]


def main() -> None:
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(
        CANDIDATES,
        max_concurrency=3,
        # Server-side filter — drops chains before they hit your dataset
        # exclude_chains=True,
    )

    # Or filter client-side after the fact:
    chains = [
        r for r in businesses
        if r.get("success") and (r.get("chain_likelihood_score") or 0) >= 50
    ]
    indies = client.filter_independents(businesses)
    unsure = [
        r for r in businesses
        if r.get("success")
        and 25 <= (r.get("chain_likelihood_score") or 0) < 50
    ]

    def _print(group, label):
        print(f"\n=== {label} ({len(group)}) ===")
        for r in group:
            score = r.get("chain_likelihood_score", 0)
            rating = r.get("rating_normalized") or "?"
            reviews = r.get("reviewsCount_int") or 0
            name = (r.get("businessName") or "(unknown)")[:40]
            lead = r.get("leadScore", "?")
            print(f"  {name:<40}  chain={score:>3}  "
                  f"{rating}\u2b50 \u00d7 {reviews:,}  lead={lead}")

    _print(indies, "INDEPENDENTS (recommended for boutique outreach)")
    _print(unsure, "UNCERTAIN (manual review)")
    _print(chains, "CHAINS (skip for indie-focused campaigns)")


if __name__ == "__main__":
    main()
