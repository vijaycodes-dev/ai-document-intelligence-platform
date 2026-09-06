from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm import LLMService
from app.services.semantic_search_service import SemanticSearchService
from app.services.document_metadata_service import DocumentMetadataService


class QuestionAnswerService:

    @staticmethod
    def ask(
        db: Session,
        question: str,
        user_id: int,
        document_id: int | None = None,
        limit: int = 5,
    ):
        # =====================================================
        # STEP 1: SEMANTIC SEARCH
        # =====================================================

        results = SemanticSearchService.search(
            db=db,
            query=question,
            user_id=user_id,
            document_id=document_id,
            limit=limit,
        )

        if not results:
            return {
                "question": question,
                "answer": (
                    "I could not find relevant information "
                    "in the available documents."
                ),
                "sources": [],
            }

        # =====================================================
        # STEP 2: GET UNIQUE DOCUMENT IDS
        # =====================================================

        document_ids = list(
            {
                chunk.document_id
                for chunk, distance in results
            }
        )

        # =====================================================
        # STEP 3: RETRIEVE METADATA
        # =====================================================

        metadata_context_parts = []

        for doc_id in document_ids:

            metadata_entries = (
                DocumentMetadataService.get_metadata(
                    db=db,
                    document_id=doc_id,
                )
            )

            if metadata_entries:

                metadata_lines = [
                    f"{item.key}: {item.value}"
                    for item in metadata_entries
                ]

                metadata_context_parts.append(
                    f"[Document {doc_id} Metadata]\n"
                    + "\n".join(metadata_lines)
                )

        metadata_context = "\n\n".join(
            metadata_context_parts
        )

        # =====================================================
        # STEP 4: BUILD DOCUMENT CHUNK CONTEXT
        # =====================================================

        chunk_context_parts = []

        for chunk, distance in results:

            chunk_context_parts.append(
                f"[Document {chunk.document_id}, "
                f"Chunk {chunk.chunk_index}]\n"
                f"{chunk.chunk_text}"
            )

        chunk_context = "\n\n".join(
            chunk_context_parts
        )

        # =====================================================
        # STEP 5: BUILD HYBRID RAG CONTEXT
        # =====================================================

        context = f"""
DOCUMENT METADATA:
{metadata_context}

DOCUMENT CONTENT:
{chunk_context}
"""

        # =====================================================
        # STEP 6: BUILD RAG PROMPT
        # =====================================================

        prompt = f"""You are a document question-answering assistant.

Use only the DOCUMENT CONTEXT to answer the QUESTION.

Rules:
- Return only the answer. Do not repeat instructions.
- Include all relevant details found in the context.
- Preserve numbers, IDs, account numbers, and codes exactly.
- Do not invent information.
- If the answer is not in the context, say: "I could not find the answer in the provided documents."

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

        # =====================================================
        # STEP 7: CALL LLM
        # =====================================================

        try:
            answer = LLMService.generate(prompt)

        except Exception as e:
            print(f"LLM ERROR: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI question answering service error: {str(e)}",
            )

        # =====================================================
        # STEP 8: RETURN ANSWER + SOURCES
        # =====================================================

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "similarity": round(1 - distance, 4),
                    "text": chunk.chunk_text,
                }
                for chunk, distance in results
            ],
        }