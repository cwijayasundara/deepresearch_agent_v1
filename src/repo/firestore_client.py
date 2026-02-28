"""Firestore repository for research reports."""

import logging

from src.types.errors import FirestoreError
from src.types.report import ResearchReport

logger = logging.getLogger(__name__)


class FirestoreRepo:
    """Async CRUD operations for research reports in Firestore."""

    def __init__(self, db: object, collection_name: str) -> None:
        self._db = db
        self.collection_name = collection_name

    def _doc_ref(self, doc_id: str) -> object:
        """Get a document reference by ID."""
        return self._db.collection(self.collection_name).document(doc_id)

    async def save_report(self, report: ResearchReport) -> None:
        """Save a research report to Firestore."""
        try:
            doc_ref = self._db.collection(self.collection_name).document(
                report.report_id
            )
            await doc_ref.set(report.model_dump(mode="json"))
            logger.info("Saved report %s", report.report_id)
        except Exception as exc:
            logger.error("Failed to save report %s: %s", report.report_id, exc)
            raise FirestoreError(
                f"Failed to save report {report.report_id}"
            ) from exc

    async def get_report(self, report_id: str) -> ResearchReport | None:
        """Get a single report by ID."""
        try:
            doc_ref = self._db.collection(self.collection_name).document(
                report_id
            )
            snapshot = await doc_ref.get()
            if not snapshot.exists:
                return None
            return ResearchReport.model_validate(snapshot.to_dict())
        except FirestoreError:
            raise
        except Exception as exc:
            logger.error("Failed to get report %s: %s", report_id, exc)
            raise FirestoreError(
                f"Failed to get report {report_id}"
            ) from exc

    def _query_ordered(self, limit: int) -> object:
        """Build an ordered query for listing reports."""
        return (
            self._db.collection(self.collection_name)
            .order_by("run_date", direction="DESCENDING")
            .limit(limit)
        )

    async def list_reports(self, limit: int = 20) -> list[ResearchReport]:
        """List reports ordered by date descending."""
        try:
            query = self._query_ordered(limit)
            docs = await query.get()
            return [
                ResearchReport.model_validate(doc.to_dict()) for doc in docs
            ]
        except Exception as exc:
            logger.error("Failed to list reports: %s", exc)
            raise FirestoreError("Failed to list reports") from exc
