"""
Quickstart: analyze a single Yelp business and print the highlights.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from yelp_analyzer import YelpAnalyzerClient


def main() -> None:
    client = YelpAnalyzerClient()  # picks up APIFY_API_TOKEN from env

    url = "https://www.yelp.com/biz/zuni-cafe-san-francisco"
    rec = client.analyze_one(url)

    print(f"\n=== {rec.get('businessName', '(unknown)')} ===")
    print(f"  Source:            {rec.get('dataSource', 'thunderbit')}")
    rating = rec.get("rating_normalized") or rec.get("rating") or "?"
    reviews = rec.get("reviewsCount_int") or rec.get("reviewsCount") or "?"
    print(f"  Rating:            {rating}\u2b50  \u00d7 {reviews} reviews")
    print(f"  Popularity:        {rec.get('popularity_score')}/100")
    print(f"  Quality tier:      {rec.get('quality_tier')}")
    print(f"  Customer segment:  {rec.get('customer_segment')}")
    print(f"  Categories:        {rec.get('categories')}")

    parsed = rec.get("parsedAddress") or {}
    print(f"  Address:           {parsed.get('street') or rec.get('address')}")
    if parsed:
        print(f"                     {parsed.get('city')}, "
              f"{parsed.get('state')} {parsed.get('zipCode')}")
    print(f"  Timezone:          {rec.get('timezone')}")
    print(f"  Neighborhood:      {rec.get('neighborhood')}")

    print(f"\n--- Hours ---")
    print(f"  Total/week:        {rec.get('hours_per_week_total')}")
    print(f"  Open weekends:     {rec.get('open_weekends')}")
    print(f"  Has 24-hour day:   {rec.get('has_24h_day')}")
    print(f"  Open right now:    {rec.get('is_open_now')}  "
          f"(timezone-aware)")

    schedule = rec.get("weekly_schedule") or []
    if schedule:
        for entry in schedule:
            print(f"    {entry['day']:10} {entry['opens']} - {entry['closes']}")

    print(f"\n--- Website ---")
    print(f"  URL:               {rec.get('website') or '(not found)'}")
    if rec.get("website_discovered_via"):
        print(f"  Discovered via:    {rec['website_discovered_via']}")
    tech = rec.get("website_tech_stack") or []
    if tech:
        print(f"  Tech stack:        {', '.join(tech)}")
    if rec.get("seo_hygiene_score") is not None:
        print(f"  SEO hygiene:       {rec['seo_hygiene_score']}/100")
        print(f"  Mobile friendly:   {rec.get('mobile_friendly')}")

    print(f"\n--- Contact ---")
    if rec.get("phoneE164"):
        print(f"  Phone (E.164):     {rec['phoneE164']}")
    emails = rec.get("emails_from_website") or rec.get("schema_emails") or []
    if emails:
        print(f"  Real emails:       {', '.join(emails[:3])}")
    elif rec.get("emails_guessed"):
        print(f"  Guessed emails:    {', '.join(rec['emails_guessed'][:3])}  "
              "(verify before sending!)")
    socials = rec.get("social_profiles") or {}
    if socials:
        print(f"  Social:")
        for platform, url in socials.items():
            print(f"    {platform:12} {url}")

    print(f"\n--- Lead score ---")
    print(f"  Score:             {rec.get('leadScore', '?')}/100")
    print(f"  Tier:              {rec.get('leadTier', '?')}")
    if rec.get("leadScoreReasons"):
        for r in rec["leadScoreReasons"]:
            print(f"    + {r}")

    if rec.get("bestContact"):
        bc = rec["bestContact"]
        print(f"\n--- Best contact ---")
        print(f"  Channel:           {bc.get('channel')}")
        print(f"  Value:             {bc.get('value')}")

    if rec.get("outreachPitch"):
        print(f"\n--- Outreach pitch ---")
        print(f"  {rec['outreachPitch']}")

    links = rec.get("outreachLinks") or {}
    if links:
        print(f"\n--- One-click outreach links ---")
        for k, v in links.items():
            print(f"  {k:30} {v[:80]}")


if __name__ == "__main__":
    main()
