
import json
import sqlite3
from pathlib import Path

from app.schemas.claim import ClaimAssessment


# Store the database in the backend folder.
DATABASE_PATH = Path(__file__).resolve().parents[2] / "freshguard.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS claim_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                claim_text TEXT NOT NULL,
                volatility TEXT NOT NULL,
                status TEXT NOT NULL,
                explanation TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                next_check_at TEXT NOT NULL,
                sources_json TEXT NOT NULL
            )
            """
        )


def save_assessments(
    assessments: list[ClaimAssessment],
) -> int:
    """Save a batch of claim assessments. Return rows saved."""

    rows = []

    for assessment in assessments:
        rows.append(
            (
                assessment.claim.claim_id,
                assessment.claim.text,
                assessment.claim.volatility.value,
                assessment.status.value,
                assessment.explanation,
                assessment.checked_at.isoformat(),
                assessment.next_check_at.isoformat(),
                json.dumps(
                    [
                        source.model_dump(mode="json")
                        for source in assessment.sources
                    ]
                ),
            )
        )

    if not rows:
        return 0

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO claim_assessments (
                claim_id,
                claim_text,
                volatility,
                status,
                explanation,
                checked_at,
                next_check_at,
                sources_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    return len(rows)


def get_latest_sources(claim_id: str) -> list[dict]:
    """Return the sources from the most recent assessment of a claim."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT sources_json
            FROM claim_assessments
            WHERE claim_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (claim_id,),
        ).fetchone()

    if row is None:
        return []

    return json.loads(row["sources_json"])


def compare_evidence(
    assessment: ClaimAssessment,
    previous_sources: list[dict],
) -> dict:
    """
    Compare current evidence with previous evidence.

    Detect:
    - Newly discovered sources
    - Sources that disappeared
    - Existing sources with changed titles or snippets
    """

    current_sources = [
        source.model_dump(mode="json")
        for source in assessment.sources
    ]

    def normalize_url(url: str) -> str:
        return url.strip().rstrip("/")

    previous_by_url = {
        normalize_url(str(source.get("url", ""))): source
        for source in previous_sources
        if source.get("url")
    }

    current_by_url = {
        normalize_url(str(source.get("url", ""))): source
        for source in current_sources
        if source.get("url")
    }

    previous_urls = set(previous_by_url)
    current_urls = set(current_by_url)

    added_urls = current_urls - previous_urls
    removed_urls = previous_urls - current_urls
    common_urls = current_urls & previous_urls

    added_sources = [
        current_by_url[url]
        for url in sorted(added_urls)
    ]

    removed_sources = [
        previous_by_url[url]
        for url in sorted(removed_urls)
    ]

    modified_sources = []

    for url in sorted(common_urls):
        old_source = previous_by_url[url]
        new_source = current_by_url[url]

        old_title = str(old_source.get("title", "")).strip()
        new_title = str(new_source.get("title", "")).strip()

        old_snippet = str(old_source.get("snippet", "")).strip()
        new_snippet = str(new_source.get("snippet", "")).strip()

        if old_title != new_title or old_snippet != new_snippet:
            modified_sources.append(
                {
                    "url": new_source.get("url", ""),
                    "previous_title": old_title,
                    "current_title": new_title,
                    "previous_snippet": old_snippet,
                    "current_snippet": new_snippet,
                }
            )

    changed = bool(
        added_sources or removed_sources or modified_sources
    )

    return {
        "changed": changed,
        "added_sources": added_sources,
        "removed_sources": removed_sources,
        "modified_sources": modified_sources,
    }


def evidence_changed(
    assessment: ClaimAssessment,
    previous_sources: list[dict],
) -> bool:
    """Backward-compatible boolean evidence comparison."""

    return compare_evidence(assessment, previous_sources)["changed"]


def get_claim_history(claim_id: str) -> list[dict]:
    """Return all saved assessments for a claim, newest first."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                claim_id,
                claim_text,
                volatility,
                status,
                explanation,
                checked_at,
                next_check_at,
                sources_json
            FROM claim_assessments
            WHERE claim_id = ?
            ORDER BY id DESC
            """,
            (claim_id,),
        ).fetchall()

    history = []

    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item.pop("sources_json"))
        history.append(item)

    return history
