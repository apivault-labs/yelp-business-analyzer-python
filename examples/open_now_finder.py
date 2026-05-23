"""
Find Yelp businesses that are open right now (timezone-aware).

The actor parses the address to extract the US state, derives the IANA
timezone (PST/EST/CST/MST/...), and uses it to compute `is_open_now`
correctly. No more "everything looks closed because we used UTC".

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/open_now_finder.py
"""

from yelp_analyzer import YelpAnalyzerClient


CANDIDATES = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",      # CA — PT
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",           # CA — PT
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",      # NY — ET
    "https://www.yelp.com/biz/franklin-barbecue-austin-2",        # TX — CT
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",   # CA — PT
]


def main() -> None:
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(CANDIDATES, max_concurrency=3)

    open_now = client.filter_open_now(businesses)
    closed = [r for r in businesses
              if r.get("success") and r.get("is_open_now") is False]
    unknown = [r for r in businesses
               if r.get("success") and r.get("is_open_now") is None]

    print(f"\n=== OPEN NOW ({len(open_now)}) ===")
    for r in open_now:
        tz = r.get("timezone", "?")
        name = (r.get("businessName") or "?")[:40]
        rating = r.get("rating_normalized") or "?"
        print(f"  ✅ {name:<40}  {rating}\u2b50  {tz}")

    print(f"\n=== CLOSED ({len(closed)}) ===")
    for r in closed:
        tz = r.get("timezone", "?")
        name = (r.get("businessName") or "?")[:40]
        # Show today's hours so the user can see when it'll open
        schedule = r.get("weekly_schedule") or []
        today_hours = "—"
        from datetime import datetime
        try:
            from zoneinfo import ZoneInfo
            today_idx = datetime.now(ZoneInfo(tz)).weekday() if tz else 0
        except Exception:
            today_idx = 0
        DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]
        today_name = DAY_NAMES[today_idx]
        for entry in schedule:
            if entry.get("day") == today_name:
                today_hours = f"{entry['opens']}-{entry['closes']}"
                break
        print(f"  ❌ {name:<40}  today: {today_hours}  ({tz})")

    if unknown:
        print(f"\n=== UNKNOWN ({len(unknown)}) ===")
        for r in unknown:
            print(f"  ? {(r.get('businessName') or '?')[:40]}  "
                  "(no schedule data)")


if __name__ == "__main__":
    main()
