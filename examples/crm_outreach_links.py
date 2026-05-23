"""
Generate one-click outreach URLs and write them to a CSV ready for
HubSpot / Pipedrive / Salesforce / Apollo import.

Each row gets:
- mailto:  with auto-generated subject + outreach pitch as body
- tel:     click-to-call (E.164 normalized)
- sms:
- WhatsApp with auto-pasted pitch
- LinkedIn people search for the business owner / founder / CEO
- Google search for the business name + city
- Yelp search for competitors in the same neighborhood

Drop the CSV into your CRM, paste the URLs into a sequence, hit send.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/crm_outreach_links.py > outreach.csv
"""

import csv
import sys

from yelp_analyzer import YelpAnalyzerClient


PROSPECTS = [
    "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    "https://www.yelp.com/biz/tartine-bakery-san-francisco",
    "https://www.yelp.com/biz/diptyque-san-francisco-2",
]

CSV_FIELDS = [
    "businessName",
    "leadScore",
    "leadTier",
    "bestContact",
    "outreachPitch",
    "mailto_url",
    "tel_url",
    "sms_url",
    "whatsapp_url",
    "linkedin_search_url",
    "google_search_url",
    "yelp_competitors_url",
]


def main() -> None:
    client = YelpAnalyzerClient()
    businesses, _ = client.analyze(PROSPECTS, max_concurrency=3)

    writer = csv.DictWriter(sys.stdout, fieldnames=CSV_FIELDS)
    writer.writeheader()

    for r in businesses:
        if not r.get("success"):
            continue
        links = r.get("outreachLinks") or {}
        bc = r.get("bestContact") or {}
        writer.writerow({
            "businessName": r.get("businessName"),
            "leadScore": r.get("leadScore"),
            "leadTier": r.get("leadTier"),
            "bestContact": f"{bc.get('channel', '?')}: {bc.get('value', '')}",
            "outreachPitch": r.get("outreachPitch"),
            "mailto_url": (links.get("mailto_url_with_pitch")
                           or links.get("mailto_url")),
            "tel_url": links.get("tel_url"),
            "sms_url": links.get("sms_url"),
            "whatsapp_url": links.get("whatsapp_url"),
            "linkedin_search_url": links.get("linkedin_search_url"),
            "google_search_url": links.get("google_search_url"),
            "yelp_competitors_url": links.get("yelp_competitors_url"),
        })


if __name__ == "__main__":
    main()
