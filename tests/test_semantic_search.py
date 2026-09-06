from app.database.session import SessionLocal
from app.services.semantic_search_service import (
    SemanticSearchService,
)


def test_semantic_search():
    db = SessionLocal()

    try:
        results = SemanticSearchService.search(
            db=db,
            query="When is the invoice payment due?",
            document_id=2,
            limit=5,
        )

        assert isinstance(results, list)

        for chunk, distance in results:
            assert chunk.document_id == 2
            assert chunk.chunk_text
            assert distance is not None

    finally:
        db.close()