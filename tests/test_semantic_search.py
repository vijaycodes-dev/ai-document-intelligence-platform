from uuid import uuid4

from app.ai.embeddings import EmbeddingService
from app.database.session import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.services.semantic_search_service import SemanticSearchService


def test_semantic_search():
    db = SessionLocal()

    try:
        user = User(
            full_name="Test User",
            email=f"semantic-search-test-{uuid4()}@example.com",
            hashed_password="test-password",
        )
        db.add(user)
        db.flush()

        document = Document(
            filename="test.pdf",
            original_filename="test.pdf",
            file_type="pdf",
            file_size=100,
            storage_path="uploads/test.pdf",
            status="completed",
            processing_stage="completed",
            uploaded_by=user.id,
        )
        db.add(document)
        db.flush()

        chunk_text = "The invoice payment due date is January 31, 2026."

        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            chunk_text=chunk_text,
            embedding=EmbeddingService.generate_embedding(chunk_text),
        )
        db.add(chunk)
        db.commit()

        results = SemanticSearchService.search(
            db=db,
            query="When is the invoice payment due?",
            user_id=user.id,
            document_id=document.id,
            limit=5,
        )

        assert isinstance(results, list)
        assert results

        for result_chunk, distance in results:
            assert result_chunk.document_id == document.id
            assert result_chunk.chunk_text
            assert distance is not None

    finally:
        db.rollback()
        db.close()
