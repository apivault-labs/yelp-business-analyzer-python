"""
Yelp Business Analyzer — Python SDK

Official Python client for the apivault_labs/yelp-business-scraper Apify actor.
Get real-time ratings, structured weekly hours with is-open-now, website tech
stack, business listing age, popularity score, customer segment and chain
detection for any Yelp business — all in one API call.

Quick start:

    from yelp_analyzer import YelpAnalyzerClient

    client = YelpAnalyzerClient(api_token="apify_api_xxxxxx")
    result = client.analyze_one(
        "https://www.yelp.com/biz/tartine-bakery-san-francisco"
    )

    print(result["popularity_score"])
    print(result["weekly_schedule"])

See https://github.com/apivault-labs/yelp-business-analyzer-python for full docs.
"""

from .client import YelpAnalyzerClient
from .exceptions import (
    YelpAnalyzerError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "YelpAnalyzerClient",
    "YelpAnalyzerError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
