
from urllib.parse import urlparse


# Simple, explainable source-quality tiers for the FreshGuard MVP.
PRIMARY_DOMAINS = {
    "python.org",
    "pythoninstitute.org",
    "cisa.gov",
    "nist.gov",
    "cve.org",
    "nvd.nist.gov",
    "who.int",
    "pubmed.ncbi.nlm.nih.gov",
    "docs.aws.amazon.com",
    "learn.microsoft.com",
}

SECONDARY_DOMAINS = {
    "wikipedia.org",
    "geeksforgeeks.org",
    "reuters.com",
    "apnews.com",
    "bbc.com",
}

LOW_CONFIDENCE_DOMAINS = {
    "instagram.com",
    "facebook.com",
    "tiktok.com",
    "reddit.com",
    "quora.com",
    "news.ycombinator.com",
}


def get_domain(url: str) -> str:
    """Extract a normalized hostname from a URL."""

    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


def get_source_quality(url: str) -> dict:
    """
    Return an explainable source-quality tier and score.

    This is a heuristic, not a guarantee that a source is correct.
    """

    domain = get_domain(url)

    if any(
        domain == trusted or domain.endswith("." + trusted)
        for trusted in PRIMARY_DOMAINS
    ):
        return {
            "score": 3,
            "tier": "primary",
            "reason": "Recognized official or primary source domain.",
        }

    if any(
        domain == trusted or domain.endswith("." + trusted)
        for trusted in SECONDARY_DOMAINS
    ):
        return {
            "score": 2,
            "tier": "secondary",
            "reason": "Recognized secondary information source.",
        }

    if any(
        domain == low_confidence or domain.endswith("." + low_confidence)
        for low_confidence in LOW_CONFIDENCE_DOMAINS
    ):
        return {
            "score": 0,
            "tier": "low_confidence",
            "reason": "User-generated or social content; use as a lead, not strong evidence.",
        }

    return {
        "score": 1,
        "tier": "unclassified",
        "reason": "Domain has not been classified by the MVP source policy.",
    }
