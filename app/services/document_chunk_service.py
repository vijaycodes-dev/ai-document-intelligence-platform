from sqlalchemy.orm import Session

from app.ai.chunking import TextChunker
from app.ai.embeddings import EmbeddingService
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)

class DocumentChunkService:
    
    @staticmethod
    def delete_chunks(
        db: Session,
        document_id: int,
    ):
        DocumentChunkRepository.delete_by_document_id(
            db=db,
            document_id=document_id,
        )

    @staticmethod
    def create_chunks(
        db: Session,
        document_id: int,
        text: str,
    ):
        chunker = TextChunker(
            chunk_size=500,
            chunk_overlap=50,
        )

        chunks = chunker.split_text(text)

        created_chunks = []

        for index, chunk_text in enumerate(chunks):
            embedding = EmbeddingService.generate_embedding(
                chunk_text
            )

            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embedding,
            )

            db.add(chunk)
            created_chunks.append(chunk)

        db.commit()

        return created_chunks
    
