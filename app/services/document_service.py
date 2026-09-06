import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.constants import (
    ALLOWED_FILE_TYPES,
    DOCUMENT_STATUS_UPLOADED,
    MAX_UPLOAD_SIZE,
    UPLOAD_DIRECTORY,
)
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.ai.classifier import DocumentClassifier
from app.ai.ocr import OCRService   
from app.ai.extractor_manager import ExtractorManager   
from app.services.document_metadata_service import DocumentMetadataService
from app.services.summarization import summarize_text
from app.services.document_chunk_service import DocumentChunkService

class DocumentService:

    @staticmethod
    def upload_document(
        db: Session,
        file: UploadFile,
        user_id: int,
    ):

        # Validate content type
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        # Read file
        file_bytes = file.file.read()

        # Validate size
        if len(file_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 20 MB.",
            )

        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

        extension = os.path.splitext(file.filename)[1].lower()

        unique_filename = f"{uuid.uuid4()}{extension}"

        storage_path = os.path.join(
            UPLOAD_DIRECTORY,
            unique_filename,
        )

        with open(storage_path, "wb") as buffer:
            buffer.write(file_bytes)

        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_type=file.content_type,
            file_size=len(file_bytes),
            storage_path=storage_path,
            uploaded_by=user_id,
            status=DOCUMENT_STATUS_UPLOADED,
        )

        return DocumentRepository.create(db, document)
    
    @staticmethod
    def list_documents(
        db: Session,
        user_id: int,
    ):
        return DocumentRepository.get_all_by_user(
            db,
            user_id,
        )
        
    @staticmethod
    def get_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        return document
    
    @staticmethod
    def delete_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        # Delete file from storage
        if os.path.exists(document.storage_path):
            os.remove(document.storage_path)

        # Delete metadata
        DocumentRepository.delete(
            db=db,
            document=document,
        )

        return {
            "message": "Document deleted successfully."
        }
        
    @staticmethod
    def download_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        if not os.path.exists(document.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found.",
            )

        return document
    
    @staticmethod
    def extract_document_text(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        try:
            text = OCRService.extract_text(
                document.storage_path
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No text could be extracted from the document.",
            )

        except RuntimeError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document text extraction service is temporarily unavailable.",
            )

        return {
            "document_id": document.id,
            "extracted_text": text,
        }
    
    @staticmethod
    def classify_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        try:
            text = OCRService.extract_text(
                document.storage_path
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No text could be extracted from the document.",
            )

        except RuntimeError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document text extraction service is temporarily unavailable.",
            )

        try:
            document_type = DocumentClassifier.classify(text)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document classification service is temporarily unavailable.",
            )

        return {
            "document_id": document.id,
            "document_type": document_type,
        }
        
        
    @staticmethod
    def process_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        # 1. Find document
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        # 2. OCR
        try:
            text = OCRService.extract_text(
                document.storage_path
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No text could be extracted from the document.",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document text extraction service is temporarily unavailable.",
            )

        # 3. Classification
        try:
            document_type = DocumentClassifier.classify(text)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document classification service is temporarily unavailable.",
            )

        # 4. Metadata extraction
        try:
            metadata = ExtractorManager.extract(text)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document metadata extraction service is temporarily unavailable.",
            )

        # 5. Save metadata
        try:
            DocumentMetadataService.save_metadata(
                db=db,
                document_id=document.id,
                metadata=metadata,
            )
            db.commit()

        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to save document metadata.",
            )

        # 6. Chunking + embeddings
        try:
            DocumentChunkService.create_chunks(
                db=db,
                document_id=document.id,
                text=text,
            )

        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document chunking and embedding service is temporarily unavailable.",
            )

        return {
            "document_id": document.id,
            "document_type": document_type,
            "metadata": metadata,
        }
        
    @staticmethod
    def summarize_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        document = DocumentRepository.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        # 1. Extract OCR text
        try:
            text = OCRService.extract_text(
                document.storage_path
            )

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No text could be extracted from the document.",
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document text extraction service is temporarily unavailable.",
            )

        # 2. Get stored metadata
        metadata_entries = DocumentMetadataService.get_metadata(
            db=db,
            document_id=document.id,
        )

        metadata = {
            entry.key: entry.value
            for entry in metadata_entries
        }

        # 3. Generate summary using OCR + metadata
        try:
            summary = summarize_text(
                text=text,
                metadata=metadata,
            )

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(e),
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document summarization service is temporarily unavailable.",
            )

        return {
            "document_id": document.id,
            "summary": summary,
        }