# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] — 2026-05-23 — v1.4 actor support

Major SDK overhaul to expose all the features added to the underlying actor
between actor v1.0 and v1.4.

### Added — 12 new client methods

- `analyze()` returns `(businesses, summary)` tuple — the actor's aggregate
  `SUMMARY` is now read directly from the run's KV store (free, doesn't
  trigger pay-per-event), no more parsing it out of the dataset.
- `get_summary()` — fetch the SUMMARY record from the most recent run on demand
- `get_top_leads()` — fetch the `TOP_LEADS` snapshot (top 20 prospects sorted
  by `leadScore`, flattened with the highest-signal fields ready for
  CRM / Slack-bot / email-alert workflows)
- `filter_by_lead_tier(businesses, *tiers)` — `cold` / `warm` / `hot` /
  `scorching`. Default keeps `("scorching", "hot")`.
- `filter_by_quality(businesses, *tiers)` — Yelp star-rating tier filter
- `filter_by_segment(businesses, *segments)` — `budget` / `mid-range` /
  `upscale` / `luxury`
- `filter_independents(businesses, max_chain_score=25)` — drops chains
- `filter_with_email(businesses, include_guessed=False)` — real emails by
  default, opt-in to also include the 11-pattern guesses
- `filter_with_phone(businesses)` — any usable phone (E.164 or otherwise)
- `filter_open_now(businesses)` — uses the actor's timezone-aware
  `is_open_now`
- `filter_by_state(businesses, *states)` — US 2-letter state codes
- `filter_by_tech(businesses, *tech_names, match_all=False)` — match against
  the website tech stack (case-insensitive substring)

### Added — 14 new input parameters

`analyze()` now forwards every actor input flag from v1.4:

- `thunderbit_retries` — tunable retry count when Thunderbit hits transient
  block (Yelp throttle)
- `slug_fallback_on_fail` — when Thunderbit gives up, derive the business
  name from the URL slug and run the website-discovery + enrichment
  layers anyway. Recovers ~60% of failed runs into useful partial records.
- `website_discovery_fallback` — DuckDuckGo lookup when Yelp doesn't
  expose the website
- `extract_contact_enrichment` — emails (with CloudFlare decoder),
  phones, social profiles, action links
- `guess_email_patterns` — 11 likely contact addresses for the discovered
  domain (`info@`, `hello@`, `contact@`, ...)
- `extract_amenities` — 28 boolean flags
- `extract_address_parts` — street/city/state/zipCode/country + IANA
  timezone
- `extract_domain_age` — crt.sh SSL history (legitimacy signal, opt-in)
- `extract_geocoding` — Nominatim lat/lng (opt-in)
- `extract_lead_score` — leadScore + reasons + tier + bestContact
- `extract_outreach_pitch` — 15 industry-specific cold-outreach templates
- `extract_outreach_links` — one-click mailto/tel/sms/WhatsApp/
  LinkedIn-search/Google-search/Yelp-competitors URLs
- `exclude_chains` — auto-drop chains/franchises
- `export_format` — `default` (full JSON) or `csv` (sales-ready 30-column
  flat shape for HubSpot/Pipedrive/Salesforce import)

### Added — 8 new examples

- `quickstart.py` — single business, all defaults
- `bulk_analyze.py` — many businesses with summary
- `find_chains_vs_indies.py` — independent SMB filter
- `open_now_finder.py` — timezone-aware open-now
- `compare_neighborhoods.py` — neighborhood-level segment distribution
- `export_to_csv.py` — CSV export for CRM import
- `lead_scoring_pipeline.py` — full sales-ops workflow with TOP_LEADS
- `crm_outreach_links.py` — paste outreach links into HubSpot/Pipedrive
- `tech_stack_prospecting.py` — find Shopify/WordPress/OpenTable users
- `email_pattern_outreach.py` — use guessed emails for cold outreach

### Changed

- Default `timeout` raised from 600s → 900s to accommodate Thunderbit
  retries on Yelp-throttled URLs.
- `analyze_one()` keeps backward-compatible signature but no longer
  attempts to write a summary (single-URL runs don't need one).

## [0.1.0] — 2026-05-22

Initial release of the Python SDK.
