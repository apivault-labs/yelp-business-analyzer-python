"""
When the website doesn't expose a real email, the actor returns 11 likely
contact addresses (info@, hello@, contact@, support@, sales@, team@,
office@, admin@, inquiries@, reservations@, bookings@) for the discovered
domain.

This example shows how to use them safely:
- Verify each address with an email-deliverability tool (Hunter, NeverBounce,
  ZeroBounce) before sending — the actor flags them with a warning
- Send a "spray and pray" sequence with strict bounce-handling
- Or use them only as a research aid (manually pick which one to try)

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/email_pattern_outreach.py
"""

from yelp_analyzer import YelpAnalyzerClient


PROSPECTS = [
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/the-french-laundry-yountville-3",
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
]


def main() -> None:
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(PROSPECTS, max_concurrency=3,
                                   guess_email_patterns=True)

    print("\n=== Email outreach roster ===\n")
    for r in businesses:
        if not r.get("success"):
            continue

        name = r.get("businessName", "?")
        real = r.get("emails_from_website") or r.get("schema_emails") or []
        guessed = r.get("emails_guessed") or []

        print(f"\n{name}")
        if real:
            print(f"  ✅ REAL EMAILS (use these first):")
            for email in real:
                print(f"     {email}")
        elif guessed:
            print(f"  🎯 GUESSED PATTERNS (verify before sending!):")
            print(f"     Domain: {r.get('website_domain')}")
            for email in guessed[:5]:
                print(f"     {email}")
            print(f"     ... + {len(guessed) - 5} more")
            print(f"  ⚠ Warning: {r.get('emails_guessed_warning')}")
        else:
            print(f"  ⛔ No emails available, no website found.")
            socials = r.get("social_profiles") or {}
            if socials:
                print(f"     Try DM instead:")
                for plat, url in list(socials.items())[:2]:
                    print(f"       {plat}: {url}")

        if r.get("outreachPitch"):
            print(f"  Suggested pitch:")
            print(f"     \"{r['outreachPitch'][:120]}...\"")


if __name__ == "__main__":
    main()
