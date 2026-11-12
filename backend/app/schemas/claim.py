
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class Volatility(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT = "insufficient"
    NEEDS_RECHECK = "needs_recheck"


class Claim(BaseModel):
    claim_id: str
    text: str = Field(min_length=5)
    volatility: Volatility = Volatility.MEDIUM


class EvidenceSource(BaseModel):
    title: str
    url: HttpUrl
    snippet: str = ""
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ClaimAssessment(BaseModel):
    claim: Claim
    status: EvidenceStatus
    explanation: str
    next_check_at: datetime
    sources: list[EvidenceSource] = Field(default_factory=list)
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
