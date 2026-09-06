from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services.document_service import DocumentService
from unittest.mock import MagicMock, patch

def test_process_document_not_found():
    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=None,
                document_id=999,
                user_id=1,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Document not found."


def test_process_document_ocr_no_text():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        side_effect=ValueError("No text"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=None,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 422


def test_process_document_ocr_failure():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        side_effect=RuntimeError("OCR failed"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=None,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503


def test_process_document_classification_failure():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="sample document text",
    ), patch(
        "app.services.document_service.DocumentClassifier.classify",
        side_effect=RuntimeError("Classification failed"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=None,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503
    
    
    
def test_process_document_metadata_extraction_failure():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="sample document text",
    ), patch(
        "app.services.document_service.ExtractorManager.extract",
        side_effect=RuntimeError("Metadata extraction failed"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=None,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503
    assert (
        exc.value.detail
        == "Document metadata extraction service is temporarily unavailable."
    )
    
    
def test_process_document_metadata_save_failure():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    db = MagicMock()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="sample document text",
    ), patch(
        "app.services.document_service.DocumentClassifier.classify",
        return_value="invoice",
    ), patch(
        "app.services.document_service.ExtractorManager.extract",
        return_value={"invoice_number": "INV-001"},
    ), patch(
        "app.services.document_service.DocumentMetadataService.save_metadata",
        side_effect=RuntimeError("Database error"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=db,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 500
    assert exc.value.detail == "Unable to save document metadata."

    db.rollback.assert_called_once()
    
    
def test_process_document_chunking_embedding_failure():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    db = MagicMock()

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="sample document text",
    ), patch(
        "app.services.document_service.DocumentClassifier.classify",
        return_value="invoice",
    ), patch(
        "app.services.document_service.ExtractorManager.extract",
        return_value={"invoice_number": "INV-001"},
    ), patch(
        "app.services.document_service.DocumentMetadataService.save_metadata",
    ), patch(
        "app.services.document_service.DocumentChunkService.create_chunks",
        side_effect=RuntimeError("Embedding service failed"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.process_document(
                db=db,
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503
    assert (
        exc.value.detail
        == "Document chunking and embedding service is temporarily unavailable."
    )

    db.rollback.assert_called_once()
    

def test_process_document_success():
    document = type(
        "Document",
        (),
        {
            "id": 1,
            "storage_path": "test.pdf",
        },
    )()

    db = MagicMock()

    metadata = {
        "invoice_number": "INV-001",
        "total_amount": "100.00",
    }

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="Sample invoice text",
    ), patch(
        "app.services.document_service.DocumentClassifier.classify",
        return_value="invoice",
    ), patch(
        "app.services.document_service.ExtractorManager.extract",
        return_value=metadata,
    ), patch(
        "app.services.document_service.DocumentMetadataService.save_metadata",
    ) as mock_save_metadata, patch(
        "app.services.document_service.DocumentChunkService.create_chunks",
    ) as mock_create_chunks:

        result = DocumentService.process_document(
            db=db,
            document_id=1,
            user_id=1,
        )

    assert result["document_id"] == 1
    assert result["document_type"] == "invoice"
    assert result["metadata"] == metadata

    mock_save_metadata.assert_called_once_with(
        db=db,
        document_id=1,
        metadata=metadata,
    )

    mock_create_chunks.assert_called_once_with(
        db=db,
        document_id=1,
        text="Sample invoice text",
    )