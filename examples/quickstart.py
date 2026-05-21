"""
Quickstart: analyze a single Yelp business.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from yelp_analyzer import YelpAnalyzerClient


def main() -> None:
    client = YelpAnalyzerClient()  # picks up APIFY_API_TOKEN from env

    url = "https://www.yelp.com/biz/tartine-bakery-san-francisco"
    rec = client.analyze_one(url)

    print(f"\n=== {rec['businessName']} ===")
    print(f"  Rating:            {rec.get('rating')}\u2b50  \u00d7 {rec.get('reviewsCount')} reviews")
    print(f"  Popularity:        {rec.get('popularity_score')}/100")
    print(f"  Quality:           {rec.get('quality_tier')}")
    print(f"  Customer segment:  {rec.get('customer_segment')}")
    print(f"  Categories:        {rec.get('categories')}")
    print(f"  Address:           {rec.get('address')}")
    print(f"  Neighborhood:      {rec.get('neighborhood')}")
    print(f"  Online presence:   {rec.get('online_presence_score')}/100")
    print(f"  Chain likelihood:  {rec.get('chain_likelihood_score')}/100")

    print(f"\nHours:")
    print(f"  Total/week:        {rec.get('hours_per_week_total')}")
    print(f"  Days open:         {rec.get('days_open_count')}")
    print(f"  Open weekends:     {rec.get('open_weekends')}")
    print(f"  Has 24-hour day:   {rec.get('has_24h_day')}")
    print(f"  Open right now:    {rec.get('is_open_now')}")

    schedule = rec.get("weekly_schedule") or []
    if schedule:
        print(f"\nWeekly schedule:")
        for entry in schedule:
            print(f"  {entry['day']:10} {entry['opens']} - {entry['closes']}")

    age = rec.get("business_listing_age_years")
    if age is not None:
        print(f"\nListing age:       {age} years (since {rec.get('estimated_first_listed_year')})")

    tech = rec.get("website_tech_stack") or []
    if tech:
        print(f"\nWebsite tech stack: {', '.join(tech)}")


if __name__ == "__main__":
    main()
