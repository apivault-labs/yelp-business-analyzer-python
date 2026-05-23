"""
Full sales-ops pipeline: bulk-analyze, sort by leadScore, filter by tier,
read TOP_LEADS from KV store, and group results by lead tier.

Run this as a daily cron / GitHub Action. Pipe TOP_LEADS to Slack to
generate a "today's top prospects" digest.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/lead_scoring_pipeline.py
"""

import json
from collections import Counter

from yelp_analyzer import YelpAnalyzerClient


YELP_URLS = [
    # ~your prospect list — paste 100s of URLs here
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/diptyque-san-francisco-2",
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/blue-bottle-coffee-san-francisco-3",
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",
    "https://www.yelp.com/biz/lazy-bear-san-francisco",
]


def main() -> None:
    client = YelpAnalyzerClient(timeout=900)
    print(f"Analyzing {len(YELP_URLS)} businesses "
          f"(${client.estimate_cost(len(YELP_URLS))})...\n")

    businesses, summary = client.analyze(
        YELP_URLS,
        max_concurrency=3,
        thunderbit_retries=2,
        slug_fallback_on_fail=True,
        # Strict prospecting: drop chains, keep only those with website
        exclude_chains=False,  # toggle on for SMB-only campaigns
    )

    successful = [r for r in businesses if r.get("success")]
    print(f"\nResults: {len(successful)}/{len(businesses)} successful")

    # Count by tier
    by_tier = Counter(r.get("leadTier", "?") for r in successful)
    print(f"\nLead tier distribution: {dict(by_tier)}")

    # The most-actionable subset
    hot_prospects = client.filter_by_lead_tier(
        successful, "scorching", "hot",
    )
    print(f"\n=== Hot/scorching prospects ({len(hot_prospects)}) ===")
    for r in sorted(hot_prospects,
                    key=lambda x: -(x.get("leadScore") or 0)):
        print(f"\n  {r['businessName']}  ({r.get('leadScore')}/100, "
              f"{r.get('leadTier')})")
        for reason in (r.get("leadScoreReasons") or [])[:5]:
            print(f"    + {reason}")
        bc = r.get("bestContact") or {}
        if bc:
            print(f"    Best contact: {bc.get('channel')} → {bc.get('value')}")
        pitch = r.get("outreachPitch")
        if pitch:
            print(f"    Pitch: {pitch[:120]}...")

    # TOP_LEADS — pre-flattened for digest / Slack / email
    top = client.get_top_leads()
    if top and top.get("top_leads"):
        print(f"\n=== TOP {top['count']} LEADS (sales digest) ===")
        # Save the raw JSON so a Slack bot can post it later
        with open("top_leads.json", "w", encoding="utf-8") as f:
            json.dump(top, f, indent=2, ensure_ascii=False)
        print("  Saved → top_leads.json")
        for lead in top["top_leads"][:5]:
            print(f"  • {lead['businessName']:<40}  "
                  f"score={lead['leadScore']}  "
                  f"contact={lead.get('bestContact', {}).get('value', 'N/A')}")

    # Aggregate health metrics
    if summary:
        print(f"\n=== SUMMARY ===")
        print(f"  Avg lead score:         {summary.get('avg_lead_score')}")
        print(f"  With website alive:     {summary.get('with_website_alive_pct')}%")
        print(f"  With real emails:       {summary.get('with_emails_pct')}%")
        print(f"  With social profiles:   {summary.get('with_social_profiles_pct')}%")


if __name__ == "__main__":
    main()
