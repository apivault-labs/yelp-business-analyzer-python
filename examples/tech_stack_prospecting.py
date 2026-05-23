"""
Find prospects by website tech stack — match-fit lead generation.

Examples:
- Toast/Square/OpenTable users → reservation-tech upsells
- WordPress restaurants → plugin / website redesign pitches
- Shopify-running businesses → e-commerce add-ons
- Stores without HSTS → security audit lead

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/tech_stack_prospecting.py
"""

from yelp_analyzer import YelpAnalyzerClient


PROSPECTS = [
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/diptyque-san-francisco-2",
    "https://www.yelp.com/biz/blue-bottle-coffee-san-francisco-3",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/momofuku-noodle-bar-new-york",
]


def main() -> None:
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(PROSPECTS, max_concurrency=3)

    # Find restaurants using OpenTable / Resy / Tock — reservation-tech ICP
    reservation_users = client.filter_by_tech(
        businesses, "OpenTable", "Resy", "Tock", "SevenRooms",
    )
    print(f"\n=== Reservation tech users ({len(reservation_users)}) ===")
    for r in reservation_users:
        tech = r.get("website_tech_stack") or []
        print(f"  {r['businessName']:<40}  → {', '.join(tech)}")
        if r.get("bestContact"):
            print(f"    Best contact: {r['bestContact']['value']}")

    # WordPress sites — plugin / redesign pitch
    wp_users = client.filter_by_tech(businesses, "WordPress")
    print(f"\n=== WordPress sites ({len(wp_users)}) ===")
    for r in wp_users:
        print(f"  {r['businessName']}")

    # Shopify-running businesses — e-commerce add-on ICP
    shopify_users = client.filter_by_tech(businesses, "Shopify")
    print(f"\n=== Shopify users ({len(shopify_users)}) ===")
    for r in shopify_users:
        print(f"  {r['businessName']}")

    # Combo filter: restaurants WITH OpenTable AND with public emails
    # — premium-margin opportunity
    print(f"\n=== Restaurants on OpenTable WITH public email "
          "(highest-intent SMBs) ===")
    high_intent = client.filter_with_email(
        client.filter_by_tech(businesses, "OpenTable"),
    )
    for r in high_intent:
        emails = (r.get("emails_from_website")
                  or r.get("schema_emails") or [])
        print(f"  {r['businessName']:<40}  → {emails[0] if emails else '?'}")

    # Sites without modern security (low-hanging upsell for security agencies)
    no_hsts = [
        r for r in businesses
        if r.get("success") and r.get("website_alive")
        and not r.get("website_has_hsts")
    ]
    print(f"\n=== Live sites WITHOUT HSTS ({len(no_hsts)}) ===")
    print("  These businesses can pay you to harden their security posture.")
    for r in no_hsts:
        print(f"  {r['businessName']:<40}  ({r.get('website_domain')})")


if __name__ == "__main__":
    main()
