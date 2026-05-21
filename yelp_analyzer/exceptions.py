"""Exception classes for the Yelp Business Analyzer SDK."""


class YelpAnalyzerError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(YelpAnalyzerError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(YelpAnalyzerError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(YelpAnalyzerError):
    """Raised when the actor run does not finish within the allowed timeout."""
