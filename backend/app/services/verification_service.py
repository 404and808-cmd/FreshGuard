from datetime import datetime, timezone

from app.services.recheck_policy import calculate_next_check
from app.services.source_quality import get_source_quality
from app.schemas.claim import (
    Claim,
    ClaimAssessment,
    EvidenceSource,
    EvidenceStatus,
    Volatility,
)
from app.services.gemini_client import GeminiClaimExtractor
from app.services.tavily_client import TavilyClient


class VerificationService:
    def __init__(self):
        self.extractor = GeminiClaimExtractor()
        self.search_client = TavilyClient()

    async def verify_text(self, text: str) -> list[ClaimAssessment]:
        extraction = self.extractor.extract_claims(text)
        assessments = []

        for index, extracted_claim in enumerate(extraction.claims, start=1):
            claim = Claim(
                claim_id=f"claim-{index}",
                text=extracted_claim.text,
                volatility=Volatility(extracted_claim.volatility.lower()),
            )

            search_response = await self.search_client.search(
                query=claim.text,
                max_results=5,
            )

            raw_results = search_response.get("results", [])

            sources = [
                EvidenceSource(
                    title=result.get("title") or "Untitled source",
                    url=result["url"],
                    snippet=result.get("content") or result.get("snippet") or "",
                )
                for result in raw_results
                if result.get("url")
            ]

            # Attach source quality to evidence sent to Gemini.
            evidence_for_model = [
                {
                    "title": source.title,
                    "url": str(source.url),
                    "snippet": source.snippet,
                    "quality": get_source_quality(str(source.url)),
                }
                for source in sources
            ]

            if evidence_for_model:
                verdict = self.extractor.assess_claim(
                    claim_text=claim.text,
                    evidence=evidence_for_model,
                )

                status = verdict.status
                explanation = verdict.explanation

                # Only primary and secondary sources count as
                # credible evidence for establishing a supported claim.
                credible_sources = [
                    source
                    for source in sources
                    if get_source_quality(str(source.url))["score"] >= 2
                ]

                # Prevent low-confidence sources alone from supporting
                # a claim, even if Gemini labels it as supported.
                if (
                    status == EvidenceStatus.SUPPORTED
                    and not credible_sources
                ):
                    status = EvidenceStatus.INSUFFICIENT
                    explanation = (
                        "The claim may be accurate, but the retrieved evidence "
                        "comes only from low-confidence or unclassified sources. "
                        "FreshGuard requires at least one recognized primary or "
                        "secondary source before marking a claim as supported."
                    )

            else:
                status = EvidenceStatus.INSUFFICIENT
                explanation = (
                    "The search returned no usable evidence sources."
                )

            checked_at = datetime.now(timezone.utc)
            next_check_at = calculate_next_check(
                volatility=claim.volatility.value,
                checked_at=checked_at,
            )

            assessments.append(
                ClaimAssessment(
                    claim=claim,
                    status=status,
                    explanation=explanation,
                    sources=sources,
                    checked_at=checked_at,
                    next_check_at=next_check_at,
                )
            )

        return assessments