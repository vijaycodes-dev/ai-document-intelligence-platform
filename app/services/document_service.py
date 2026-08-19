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
                status_code=404,
                detail="Document not found."
            )

        text = OCRService.extract_text(
            document.storage_path
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

        text = OCRService.extract_text(document.storage_path)

        document_type = DocumentClassifier.classify(text)

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

        text = OCRService.extract_text(
            document.storage_path
        )

        document_type = DocumentClassifier.classify(text)

        metadata = ExtractorManager.extract(text)

        DocumentMetadataService.save_metadata(
            db=db,
            document_id=document.id,
            metadata=metadata,
        )

        db.commit()

        return {
            "document_id": document.id,
            "document_type": document_type,
            "metadata": metadata,
        }