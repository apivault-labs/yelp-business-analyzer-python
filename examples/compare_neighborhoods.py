"""
Compare neighborhoods or cities by aggregate signals.

Run the same query against businesses in different neighborhoods and look at:
- Average lead score
- Customer segment distribution
- Tech stack adoption (% using OpenTable / Toast / Stripe)
- Open-now ratio
- Chain density

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/compare_neighborhoods.py
"""

from collections import Counter

from yelp_analyzer import YelpAnalyzerClient


# Toy lists. In a real workflow you'd source these from a Yelp search
# (find_desc + find_loc) — every Yelp page link returns its neighborhood
# field as part of `neighborhood`.
GROUPS = {
    "Mission (SF)": [
        "https://www.yelp.com/biz/tartine-bakery-san-francisco",
        "https://www.yelp.com/biz/foreign-cinema-san-francisco",
        "https://www.yelp.com/biz/lazy-bear-san-francisco",
    ],
    "Downtown LA": [
        "https://www.yelp.com/biz/bestia-los-angeles",
        "https://www.yelp.com/biz/bottega-louie-los-angeles",
        "https://www.yelp.com/biz/grand-central-market-los-angeles-2",
    ],
}


def summarize(label: str, results: list[dict]) -> None:
    successful = [r for r in results if r.get("success")]
    if not successful:
        print(f"\n[{label}] no successful records")
        return

    avg_lead = sum(r.get("leadScore", 0) for r in successful) / len(successful)
    avg_pop = (sum(r.get("popularity_score") or 0 for r in successful)
               / len(successful))
    open_now = sum(1 for r in successful if r.get("is_open_now") is True)
    chains = sum(1 for r in successful
                 if (r.get("chain_likelihood_score") or 0) >= 50)
    segments = Counter(r.get("customer_segment", "unknown") for r in successful)
    tech = Counter()
    for r in successful:
        for t in (r.get("website_tech_stack") or []):
            tech[t] += 1

    print(f"\n=== {label} ({len(successful)} businesses) ===")
    print(f"  Avg lead score:   {avg_lead:.1f}")
    print(f"  Avg popularity:   {avg_pop:.1f}")
    print(f"  Open now:         {open_now}/{len(successful)}")
    print(f"  Chains detected:  {chains}/{len(successful)}")
    print(f"  Segments:         {dict(segments)}")
    if tech:
        print(f"  Tech adoption (top 5):")
        for name, count in tech.most_common(5):
            pct = 100 * count / len(successful)
            print(f"    {name:25}  {count:>3}/{len(successful):<3}  ({pct:.0f}%)")


def main() -> None:
    client = YelpAnalyzerClient()
    for label, urls in GROUPS.items():
        print(f"\nAnalyzing {label}...")
        businesses, _ = client.analyze(urls, max_concurrency=3)
        summarize(label, businesses)


if __name__ == "__main__":
    main()
