"""
YelpAnalyzerClient — synchronous wrapper around the Apify
``apivault_labs/yelp-business-scraper`` actor (v1.4).

The actor handles all heavy work (Thunderbit + retry, slug-based fallback
when Yelp throttles, DuckDuckGo website discovery, tech-stack detection
across 50+ platforms, CloudFlare email decoder, JSON-LD schema.org parsing,
SEO + mobile audit, address parsing with timezone derivation, lead score,
industry-specific outreach pitch generation, and one-click outreach links)
on Apify infrastructure. This client forwards inputs, polls until the run
finishes, then downloads the dataset and exposes friendly filters and
helpers for sales-ops workflows.

Pricing: $0.003 per business ($3 / 1000). All enrichment included.

Quick start:

    from yelp_analyzer import YelpAnalyzerClient

    client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")

    businesses, summary = client.analyze([
        "https://www.yelp.com/biz/tartine-bakery-san-francisco",
        "https://www.yelp.com/biz/zuni-cafe-san-francisco",
    ])
    for b in client.filter_by_lead_tier(businesses, "hot", "scorching"):
        print(b["businessName"], b["leadScore"], b.get("bestContact"))
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable, Sequence

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    YelpAnalyzerError,
)


ACTOR_ID = "apivault_labs~yelp-business-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

PRICE_PER_BUSINESS_USD = 0.003


class YelpAnalyzerClient:
    """Synchronous client for the Yelp Business Analyzer Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 900
        (15 min) — typical runs finish in 15-60 seconds, but Thunderbit
        retries on a throttled Yelp pool can extend the tail.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 900,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "yelp-business-analyzer-python/0.2.0",
        })
        self._last_run_id: str | None = None
        self._last_dataset_id: str | None = None
        self._last_kvs_id: str | None = None

    # ------------------------------------------------------------------ public

    def analyze(
        self,
        business_urls: Iterable[str],
        *,
        max_concurrency: int = 2,
        timeout_per_business: int = 180,
        thunderbit_retries: int = 2,
        slug_fallback_on_fail: bool = True,
        extract_core: bool = True,
        extract_hours_intel: bool = True,
        extract_website: bool = True,
        website_discovery_fallback: bool = True,
        extract_contact_enrichment: bool = True,
        guess_email_patterns: bool = True,
        extract_amenities: bool = True,
        extract_address_parts: bool = True,
        extract_age: bool = True,
        extract_domain_age: bool = False,
        extract_geocoding: bool = False,
        extract_derived_signals: bool = True,
        extract_lead_score: bool = True,
        extract_outreach_pitch: bool = True,
        extract_outreach_links: bool = True,
        exclude_chains: bool = False,
        export_format: str = "default",
        write_summary: bool = True,
        actor_timeout_secs: int = 600,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Analyze a batch of Yelp business URLs.

        Returns
        -------
        tuple[list[dict], dict | None]
            ``(businesses, summary)``. ``summary`` is the aggregate stats
            record (avg ratings, segment distribution, top tech detected,
            chain count, etc.) or ``None`` for single-URL runs. The
            summary is also retrievable via :py:meth:`get_summary`.

        See README for the full output schema (40+ fields per business).
        """
        urls = [u for u in business_urls if u and u.strip()]
        if not urls:
            raise ValueError("business_urls must contain at least one non-empty URL")

        if export_format not in ("default", "csv"):
            raise ValueError(
                f"export_format must be 'default' or 'csv', got {export_format!r}"
            )

        payload = {
            "businessUrls": urls,
            "maxConcurrency": max(1, min(5, int(max_concurrency))),
            "timeout": max(60, min(300, int(timeout_per_business))),
            "thunderbitRetries": max(0, min(5, int(thunderbit_retries))),
            "slugFallbackOnFail": bool(slug_fallback_on_fail),
            "extractCore": bool(extract_core),
            "extractHoursIntel": bool(extract_hours_intel),
            "extractWebsite": bool(extract_website),
            "websiteDiscoveryFallback": bool(website_discovery_fallback),
            "extractContactEnrichment": bool(extract_contact_enrichment),
            "guessEmailPatterns": bool(guess_email_patterns),
            "extractAmenities": bool(extract_amenities),
            "extractAddressParts": bool(extract_address_parts),
            "extractAge": bool(extract_age),
            "extractDomainAge": bool(extract_domain_age),
            "extractGeocoding": bool(extract_geocoding),
            "extractDerivedSignals": bool(extract_derived_signals),
            "extractLeadScore": bool(extract_lead_score),
            "extractOutreachPitch": bool(extract_outreach_pitch),
            "extractOutreachLinks": bool(extract_outreach_links),
            "excludeChains": bool(exclude_chains),
            "exportFormat": export_format,
            "writeSummary": bool(write_summary),
        }

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        self._last_run_id = run_id
        self._last_dataset_id = run.get("defaultDatasetId")
        self._last_kvs_id = run.get("defaultKeyValueStoreId")
        records = self._fetch_dataset(self._last_dataset_id)

        # The actor writes the SUMMARY into the KV store (free, doesn't
        # add to the dataset). Try to fetch it for convenience.
        summary = None
        if write_summary and len(urls) > 1 and self._last_kvs_id:
            summary = self._fetch_kv_record(self._last_kvs_id, "SUMMARY")

        return records, summary

    def analyze_one(self, business_url: str, **kwargs: Any) -> dict[str, Any]:
        """Convenience wrapper for analyzing a single Yelp URL.

        Returns the result record. Raises ``ActorRunError`` if no record is
        produced — the URL might not be a valid Yelp business page.
        """
        records, _ = self.analyze([business_url], write_summary=False, **kwargs)
        if not records:
            raise ActorRunError(
                f"Actor returned no records for {business_url!r} — "
                "the URL might not be a valid Yelp business page."
            )
        return records[0]

    # ------------------------------------------------------------------ KV helpers

    def get_summary(self) -> dict[str, Any] | None:
        """Fetch the aggregate ``SUMMARY`` record from the most recent run.

        Available after :py:meth:`analyze` has been called with more than
        one URL and ``write_summary=True`` (the default).
        """
        if not self._last_kvs_id:
            return None
        return self._fetch_kv_record(self._last_kvs_id, "SUMMARY")

    def get_top_leads(self) -> dict[str, Any] | None:
        """Fetch the ``TOP_LEADS`` snapshot from the most recent run.

        Returns a dict with:
        - ``top_leads``: list of up to 20 prospects sorted by leadScore,
          flattened with the highest-signal fields (businessName, city,
          state, leadScore, leadTier, phoneE164, primaryEmail, instagram,
          bestContact, outreachPitch, mailtoUrl, whatsappUrl, ...)
        - ``count``: int
        - ``generated_at``: ISO timestamp
        """
        if not self._last_kvs_id:
            return None
        return self._fetch_kv_record(self._last_kvs_id, "TOP_LEADS")

    # ------------------------------------------------------------------ filters

    def filter_by_lead_tier(
        self,
        businesses: Sequence[dict[str, Any]],
        *tiers: str,
    ) -> list[dict[str, Any]]:
        """Filter to businesses whose ``leadTier`` is in the requested set.

        Tiers (high to low): ``"scorching"`` (≥75), ``"hot"`` (55-74),
        ``"warm"`` (35-54), ``"cold"`` (<35). Pass one or more — they are
        OR'd together. With no arguments, defaults to ``("scorching", "hot")``.
        """
        if not tiers:
            tiers = ("scorching", "hot")
        wanted = {t.lower() for t in tiers}
        return [
            r for r in businesses
            if (r.get("leadTier") or "").lower() in wanted
        ]

    def filter_by_quality(
        self,
        businesses: Sequence[dict[str, Any]],
        *tiers: str,
    ) -> list[dict[str, Any]]:
        """Filter by ``quality_tier`` (``"exceptional"`` ≥4.5, ``"great"`` ≥4.0,
        ``"good"`` ≥3.5, ``"fair"`` ≥2.5, else ``"poor"``)."""
        if not tiers:
            tiers = ("exceptional", "great")
        wanted = {t.lower() for t in tiers}
        return [
            r for r in businesses
            if (r.get("quality_tier") or "").lower() in wanted
        ]

    def filter_by_segment(
        self,
        businesses: Sequence[dict[str, Any]],
        *segments: str,
    ) -> list[dict[str, Any]]:
        """Filter by ``customer_segment`` (``"budget"``, ``"mid-range"``,
        ``"upscale"``, ``"luxury"``)."""
        if not segments:
            return list(businesses)
        wanted = {s.lower() for s in segments}
        return [
            r for r in businesses
            if (r.get("customer_segment") or "").lower() in wanted
        ]

    def filter_independents(
        self,
        businesses: Sequence[dict[str, Any]],
        max_chain_score: int = 25,
    ) -> list[dict[str, Any]]:
        """Filter to independent businesses (skips chains and franchises).

        Default keeps only ``chain_likelihood_score`` < 25.
        """
        return [
            r for r in businesses
            if (r.get("chain_likelihood_score") or 0) < max_chain_score
        ]

    def filter_with_email(
        self,
        businesses: Sequence[dict[str, Any]],
        include_guessed: bool = False,
    ) -> list[dict[str, Any]]:
        """Filter to businesses where at least one email was found.

        By default only requires a *real* email scraped from the website
        or JSON-LD. Set ``include_guessed=True`` to also accept the
        ``emails_guessed[]`` patterns.
        """
        out: list[dict[str, Any]] = []
        for r in businesses:
            if r.get("emails_from_website") or r.get("schema_emails"):
                out.append(r)
            elif include_guessed and r.get("emails_guessed"):
                out.append(r)
        return out

    def filter_with_phone(
        self,
        businesses: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Filter to businesses with a usable phone number (E.164 normalized
        or website-scraped)."""
        return [
            r for r in businesses
            if r.get("phoneE164")
            or r.get("phone")
            or r.get("phones_from_website")
            or r.get("schema_telephones")
        ]

    def filter_open_now(
        self,
        businesses: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Filter to businesses currently open (timezone-aware when state
        is parsed; falls back to UTC otherwise)."""
        return [r for r in businesses if r.get("is_open_now") is True]

    def filter_by_state(
        self,
        businesses: Sequence[dict[str, Any]],
        *states: str,
    ) -> list[dict[str, Any]]:
        """Filter by US state (2-letter code, e.g. ``"CA"``, ``"NY"``).

        Uses ``parsedAddress.state`` first, falls back to a regex on
        the raw address string for older records.
        """
        wanted = {s.upper() for s in states if s}
        if not wanted:
            return list(businesses)
        out: list[dict[str, Any]] = []
        for r in businesses:
            parsed = r.get("parsedAddress") or {}
            st = parsed.get("state") or _state_from_address(r.get("address"))
            if st and st.upper() in wanted:
                out.append(r)
        return out

    def filter_by_tech(
        self,
        businesses: Sequence[dict[str, Any]],
        *tech_names: str,
        match_all: bool = False,
    ) -> list[dict[str, Any]]:
        """Filter to businesses whose website uses any (or all) of the
        named tech stack platforms.

        ``match_all=True`` requires every name to be present (case-insensitive
        substring match against the detected stack).
        """
        if not tech_names:
            return list(businesses)
        needles = [t.lower() for t in tech_names if t]
        out: list[dict[str, Any]] = []
        for r in businesses:
            stack = [s.lower() for s in (r.get("website_tech_stack") or [])]
            if not stack:
                continue
            if match_all:
                if all(any(n in s for s in stack) for n in needles):
                    out.append(r)
            else:
                if any(any(n in s for s in stack) for n in needles):
                    out.append(r)
        return out

    # ------------------------------------------------------------------ helpers

    def split_summary(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Separate a `_summary` aggregate record from per-business records.

        For backward compatibility with older actor versions that pushed
        the summary into the dataset itself.
        """
        per_business: list[dict[str, Any]] = []
        summary: dict[str, Any] | None = None
        for rec in records:
            if isinstance(rec, dict) and rec.get("_summary"):
                summary = rec
            else:
                per_business.append(rec)
        return per_business, summary

    def estimate_cost(self, business_count: int) -> float:
        """Return the estimated USD cost for ``business_count`` businesses."""
        return round(business_count * PRICE_PER_BUSINESS_USD, 4)

    # ------------------------------------------------------------------ private

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise YelpAnalyzerError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise YelpAnalyzerError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). The run may still be running on "
                    "Apify; increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise YelpAnalyzerError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data

    def _fetch_kv_record(self, kvs_id: str, key: str) -> dict[str, Any] | None:
        """Fetch a single KV-store record (returns None if missing)."""
        url = f"{self._base_url}/key-value-stores/{kvs_id}/records/{key}"
        try:
            r = self._session.get(url, timeout=30)
        except requests.RequestException:
            return None
        if r.status_code == 404:
            return None
        if r.status_code >= 400:
            return None
        try:
            return r.json()
        except ValueError:
            return None


# Lightweight US state extractor for older records that lack `parsedAddress`.
import re as _re  # noqa: E402


def _state_from_address(address: str | None) -> str | None:
    if not address or not isinstance(address, str):
        return None
    m = _re.search(r"\b([A-Z]{2})\b\s+\d{5}", address)
    return m.group(1) if m else None
