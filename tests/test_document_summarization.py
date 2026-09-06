import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from app.services.document_service import DocumentService


def test_summarize_document_not_found():
    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.summarize_document(
                db=MagicMock(),
                document_id=999,
                user_id=1,
            )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Document not found."


def test_summarize_document_ocr_no_text():
    document = MagicMock()
    document.id = 1
    document.storage_path = "test.pdf"

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        side_effect=ValueError("No text extracted"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.summarize_document(
                db=MagicMock(),
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == "No text could be extracted from the document."


def test_summarize_document_ocr_failure():
    document = MagicMock()
    document.id = 1
    document.storage_path = "test.pdf"

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        side_effect=RuntimeError("OCR failed"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.summarize_document(
                db=MagicMock(),
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503
    assert (
        exc.value.detail
        == "Document text extraction service is temporarily unavailable."
    )
    
def test_summarize_document_llm_validation_failure():
    document = MagicMock()
    document.id = 1
    document.storage_path = "test.pdf"

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="Sample insurance document text",
    ), patch(
        "app.services.document_service.DocumentMetadataService.get_metadata",
        return_value=[],
    ), patch(
        "app.services.document_service.summarize_text",
        side_effect=ValueError("Unable to summarize document"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.summarize_document(
                db=MagicMock(),
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 422
    assert exc.value.detail == "Unable to summarize document"
    
    
def test_summarize_document_llm_service_failure():
    document = MagicMock()
    document.id = 1
    document.storage_path = "test.pdf"

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="Sample insurance document text",
    ), patch(
        "app.services.document_service.DocumentMetadataService.get_metadata",
        return_value=[],
    ), patch(
        "app.services.document_service.summarize_text",
        side_effect=RuntimeError("LLM unavailable"),
    ):
        with pytest.raises(HTTPException) as exc:
            DocumentService.summarize_document(
                db=MagicMock(),
                document_id=1,
                user_id=1,
            )

    assert exc.value.status_code == 503
    assert (
        exc.value.detail
        == "Document summarization service is temporarily unavailable."
    )
    
    
def test_summarize_document_success():
    document = MagicMock()
    document.id = 1
    document.storage_path = "test.pdf"

    metadata_entries = [
        MagicMock(key="policy_number", value="POL-123"),
        MagicMock(key="insured_name", value="Vijay"),
        MagicMock(key="premium_amount", value="INR 18,450"),
    ]

    expected_metadata = {
        "policy_number": "POL-123",
        "insured_name": "Vijay",
        "premium_amount": "INR 18,450",
    }

    expected_summary = "This is a generated document summary."

    with patch(
        "app.services.document_service.DocumentRepository.get_by_id_and_user",
        return_value=document,
    ), patch(
        "app.services.document_service.OCRService.extract_text",
        return_value="Sample insurance policy document text",
    ), patch(
        "app.services.document_service.DocumentMetadataService.get_metadata",
        return_value=metadata_entries,
    ), patch(
        "app.services.document_service.summarize_text",
        return_value=expected_summary,
    ) as mock_summarize:

        result = DocumentService.summarize_document(
            db=MagicMock(),
            document_id=1,
            user_id=1,
        )

    assert result["document_id"] == 1
    assert result["summary"] == expected_summary

    mock_summarize.assert_called_once_with(
        text="Sample insurance policy document text",
        metadata=expected_metadata,
    )