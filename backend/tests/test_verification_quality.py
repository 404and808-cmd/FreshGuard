import asyncio
from types import SimpleNamespace

from app.schemas.claim import EvidenceStatus
from app.services.verification_service import VerificationService


class FakeExtractor:
    def extract_claims(self, text):
        return SimpleNamespace(
            claims=[
                SimpleNamespace(
                    text="A sample claim for testing.",
                    volatility="low",
                )
            ]
        )

    def assess_claim(self, claim_text, evidence):
        # Simulate Gemini returning "supported".
        return SimpleNamespace(
            status=EvidenceStatus.SUPPORTED,
            explanation="The evidence appears to support the claim.",
        )


class FakeSearchClient:
    def __init__(self, results):
        self.results = results

    async def search(self, query, max_results=5):
        return {"results": self.results}


def run_verification(results):
    service = VerificationService()
    service.extractor = FakeExtractor()
    service.search_client = FakeSearchClient(results)

    return asyncio.run(service.verify_text("Test input"))


def test_low_confidence_sources_cannot_support_claim():
    results = [
        {
            "title": "Social media post",
            "url": "https://www.instagram.com/reel/example",
            "content": "This post claims the statement is true.",
        },
        {
            "title": "Forum discussion",
            "url": "https://news.ycombinator.com/item?id=123",
            "content": "A user repeats the same claim.",
        },
    ]

    assessments = run_verification(results)

    assert assessments[0].status == EvidenceStatus.INSUFFICIENT
    assert "low-confidence" in assessments[0].explanation


def test_primary_source_allows_supported_verdict():
    results = [
        {
            "title": "Official Python information",
            "url": "https://python.org/about/",
            "content": "The official source supports the claim.",
        }
    ]

    assessments = run_verification(results)

    assert assessments[0].status == EvidenceStatus.SUPPORTED