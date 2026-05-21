"""
Find Yelp businesses that are open RIGHT NOW.

Uses the actor's UTC-aware ``is_open_now`` flag. Useful for:
- Real-time "what's open" apps
- Late-night spot finders
- Hospitality operations dashboards

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/open_now_finder.py
"""

from yelp_analyzer import YelpAnalyzerClient


CANDIDATES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/in-n-out-burger-los-angeles",
    "https://www.yelp.com/biz/joes-pizza-new-york-2",
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
]


def main() -> None:
    client = YelpAnalyzerClient()
    # Skip slow optional layers when you only need open-now status
    results = client.analyze(
        CANDIDATES,
        max_concurrency=3,
        extract_age=False,
        extract_website=False,
    )

    open_now = []
    closed_but_open_today = []
    closed = []

    for r in results:
        if not r.get("success"):
            continue
        if r.get("is_open_now"):
            open_now.append(r)
            continue
        # Was the day-of-week's window in the schedule even today?
        days_open = r.get("days_open_count") or 0
        if days_open >= 6:
            closed_but_open_today.append(r)
        else:
            closed.append(r)

    print(f"\n=== OPEN RIGHT NOW ({len(open_now)}) ===")
    for r in open_now:
        print(f"  {r['businessName']:<35} {r.get('hours_per_week_total')}h/wk")

    print(f"\n=== CLOSED NOW (regular hours / quiet day) ({len(closed_but_open_today)}) ===")
    for r in closed_but_open_today:
        print(f"  {r['businessName']:<35} {r.get('hours_per_week_total')}h/wk")

    if closed:
        print(f"\n=== UNDER 6 DAYS/WEEK ({len(closed)}) ===")
        for r in closed:
            print(f"  {r['businessName']:<35} days_open={r.get('days_open_count')}")


if __name__ == "__main__":
    main()
