from app.database.session import SessionLocal
from app.services.semantic_search_service import (
    SemanticSearchService,
)


db = SessionLocal()

try:
    results = SemanticSearchService.search(
        db=db,
        query="When is the invoice payment due?",
        document_id=2,
        limit=5,
    )

    for result in results:
        print("\nChunk:", result.chunk_index)
        print("Text:", result.chunk_text)

finally:
    db.close()