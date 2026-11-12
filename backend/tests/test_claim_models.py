from datetime import datetime, timezone

from app.schemas.claim import (
    Claim,
    ClaimAssessment,
    EvidenceStatus,
    Volatility,
)


def test_claim_creation():
    claim = Claim(
        claim_id="claim-001",
        text="Python is a programming language",
        volatility=Volatility.LOW,
    )

    assert claim.claim_id == "claim-001"
    assert claim.volatility == Volatility.LOW


def test_claim_assessment_creation():
    claim = Claim(
        claim_id="claim-002",
        text="Python is a programming language",
        volatility=Volatility.LOW,
    )

    assessment = ClaimAssessment(
        claim=claim,
        status=EvidenceStatus.INSUFFICIENT,
        explanation="No evidence was collected yet.",
        checked_at=datetime.now(timezone.utc),
        next_check_at=datetime.now(timezone.utc),
    )

    assert assessment.status == EvidenceStatus.INSUFFICIENT
    assert assessment.claim == claim
    assert assessment.next_check_at is not None
