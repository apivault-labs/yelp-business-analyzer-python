"""
Analyze many Yelp businesses in one batch + read the aggregate SUMMARY.

The actor runs them in parallel on Apify infrastructure, so a single
``analyze`` call with many URLs is faster and cheaper than calling the SDK
once per business.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/bulk_analyze.py
"""

from yelp_analyzer import YelpAnalyzerClient


BUSINESSES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/diptyque-san-francisco-2",
    "https://www.yelp.com/biz/blue-bottle-coffee-san-francisco-3",
    "https://www.yelp.com/biz/in-n-out-burger-los-angeles",
]


def main() -> None:
    client = YelpAnalyzerClient(timeout=900)
    print(f"Analyzing {len(BUSINESSES)} businesses "
          f"(estimated cost: ${client.estimate_cost(len(BUSINESSES))})...\n")

    businesses, summary = client.analyze(
        BUSINESSES,
        max_concurrency=3,
        thunderbit_retries=2,
        slug_fallback_on_fail=True,   # recover from Yelp throttle
    )

    # Per-business table sorted by lead score
    print(f"{'Name':<35} {'Rating':>7} {'Pop':>4} {'Lead':>5} {'Tier':>10}  Source")
    print("-" * 80)
    for r in sorted(businesses,
                    key=lambda x: -(x.get("leadScore") or 0)):
        if not r.get("success"):
            print(f"  ❌ {r.get('inputUrl', '?')[:60]}")
            continue
        name = (r.get("businessName") or "(unknown)")[:35]
        rating = r.get("rating_normalized") or "?"
        pop = r.get("popularity_score") or "-"
        lead = r.get("leadScore") or 0
        tier = r.get("leadTier") or "?"
        src = r.get("dataSource", "thunderbit")
        print(f"{name:<35} {str(rating):>7} {str(pop):>4} {lead:>5} {tier:>10}  {src}")

    # Aggregate summary (free, lives in the run's KV store)
    if summary:
        print(f"\n--- SUMMARY ---")
        print(f"  Successful: {summary.get('successful')}/"
              f"{summary.get('total_analyzed')}")
        print(f"  Avg rating: {summary.get('avg_rating')}")
        print(f"  Avg lead score: {summary.get('avg_lead_score')}")
        print(f"  With website: {summary.get('with_website_alive_pct')}%")
        print(f"  With emails: {summary.get('with_emails_pct')}%")
        print(f"  With socials: {summary.get('with_social_profiles_pct')}%")
        print(f"  Open now: {summary.get('open_now_count')}")
        if summary.get("by_lead_tier"):
            print(f"  Lead tiers: {summary['by_lead_tier']}")
        if summary.get("top_tech_detected"):
            print(f"  Top tech (first 5):")
            for t in summary["top_tech_detected"][:5]:
                print(f"    {t['name']:20}  {t['count']}")

    # TOP_LEADS — sales-ops snapshot, also free in KV store
    top = client.get_top_leads()
    if top and top.get("top_leads"):
        print(f"\n--- TOP {top['count']} LEADS (sorted by leadScore) ---")
        for lead in top["top_leads"][:10]:
            print(f"  {lead['businessName']:35}  "
                  f"score={lead['leadScore']}  tier={lead['leadTier']}  "
                  f"{lead.get('city', '?')}, {lead.get('state', '?')}")


if __name__ == "__main__":
    main()
