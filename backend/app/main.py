
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from app.services.source_quality import get_source_quality
from fastapi.middleware.cors import CORSMiddleware
from app.services.gemini_client import GeminiClaimExtractor
from app.services.tavily_client import TavilyClient
from app.services.verification_service import VerificationService
from app.services.database import (
    initialize_database,
    save_assessments,
    get_latest_sources,
    compare_evidence,
    get_claim_history,
)

app = FastAPI(
    title="FreshGuard API",
    description="Temporal risk intelligence for AI gateways.",
    version="0.1.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


class ExtractClaimsRequest(BaseModel):
    text: str = Field(min_length=10, max_length=10000)


@app.get("/")
def root():
    return {
        "message": "Welcome to FreshGuard API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "freshguard",
    }


@app.post("/search")
async def search_web(request: SearchRequest):
    try:
        tavily = TavilyClient()
        results = await tavily.search(
            query=request.query,
            max_results=request.max_results,
        )
        return results

    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Search provider error: {type(error).__name__}",
        )


@app.post("/extract-claims")
async def extract_claims(request: ExtractClaimsRequest):
    try:
        extractor = GeminiClaimExtractor()
        result = extractor.extract_claims(request.text)
        return result

    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Claim extraction provider error: {type(error).__name__}",
        )


@app.post("/verify")
async def verify_text(request: ExtractClaimsRequest):
    try:
        initialize_database()

        verifier = VerificationService()
        assessments = await verifier.verify_text(request.text)

        change_results = []

        for assessment in assessments:
            claim_id = assessment.claim.claim_id

            previous_sources = get_latest_sources(claim_id)

            change_report = compare_evidence(
                assessment,
                previous_sources,
            )

            # An empty previous source list means this is the first check.
            first_check = len(previous_sources) == 0

            change_results.append(
                {
                    "claim_id": claim_id,
                    "first_check": first_check,
                    "evidence_changed": not first_check and change_report["changed"],
                    **change_report,
                }
            )

        saved_count = save_assessments(assessments)
        print(f"Saved {saved_count} assessments to SQLite.")

        assessment_results = []

        for assessment in assessments:
            assessment_data = assessment.model_dump(mode="json")

            for source in assessment_data["sources"]:
                source["quality"] = get_source_quality(
                    source["url"]
                )

            assessment_results.append(assessment_data)

        return {
            "input_text": request.text,
            "claim_count": len(assessments),
            "evidence_changes": change_results,
            "assessments": assessment_results,
        }

    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Verification pipeline error: {type(error).__name__}",
        )

@app.get("/history/{claim_id}")
def claim_history(claim_id: str):
    initialize_database()

    history = get_claim_history(claim_id)

    if not history:
        raise HTTPException(
            status_code=404,
            detail="No assessment history found for this claim.",
        )

    return {
        "claim_id": claim_id,
        "total_checks": len(history),
        "history": history,
    }



@app.post("/recheck/{claim_id}")
async def recheck_claim(claim_id: str):
    initialize_database()

    history = get_claim_history(claim_id)

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Claim not found.",
        )

    claim_text = history[0]["claim_text"]

    request = ExtractClaimsRequest(text=claim_text)

    return await verify_text(request)


