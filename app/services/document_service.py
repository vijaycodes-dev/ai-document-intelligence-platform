import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.constants import (
    ALLOWED_FILE_TYPES,
    DOCUMENT_STATUS_UPLOADED,
    DOCUMENT_STATUS_PROCESSING,
    DOCUMENT_STATUS_COMPLETED,
    DOCUMENT_STATUS_FAILED,
    MAX_UPLOAD_SIZE,
    UPLOAD_DIRECTORY,
)
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.ai.classifier import DocumentClassifier
from app.ai.ocr import OCRService   
from app.ai.extractor_manager import ExtractorManager   
from app.services.document_metadata_service import DocumentMetadataService
from app.services.document_processing_log_service import (
    DocumentProcessingLogService,
)
from app.services.summarization import summarize_text
from app.services.document_chunk_service import DocumentChunkService

from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_metadata_repository import (
    DocumentMetadataRepository,
)
from app.core.constants import (
    DOCUMENT_STATUS_COMPLETED,
    DOCUMENT_STATUS_FAILED,
    DOCUMENT_STATUS_PROCESSING,
    PROCESSING_STAGE_CLASSIFICATION,
    PROCESSING_STAGE_COMPLETED,
    PROCESSING_STAGE_EMBEDDING,
    PROCESSING_STAGE_FAILED,
    PROCESSING_STAGE_METADATA,
    PROCESSING_STAGE_OCR,
)

from app.core.exceptions import DocumentProcessingError

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
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
        file_type: str | None = None,
    ):
        documents, total = (
            DocumentRepository.get_paginated_by_user(
                db=db,
                user_id=user_id,
                page=page,
                page_size=page_size,
                status=status,
                file_type=file_type,
            )
        )

        total_pages = (
            (total + page_size - 1) // page_size
            if total > 0
            else 0
        )

        return {
            "items": documents,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
        
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
    def get_processing_history(
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

        return DocumentProcessingLogService.get_history(
            db=db,
            document_id=document_id,
        )
    
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
    def mark_document_processing(
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

        if document.status == DOCUMENT_STATUS_PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document is already being processed.",
            )

        document.status = DOCUMENT_STATUS_PROCESSING
        db.commit()
        db.refresh(document)

        return document
    
    @staticmethod
    def process_document_background(
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
            raise ValueError(
                f"Document {document_id} not found."
            )

        try:
            # =============================================
            # STAGE 1: OCR
            # =============================================
            document.processing_stage = PROCESSING_STAGE_OCR
            db.commit()

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_OCR,
                status="processing",
                message="OCR processing started.",
            )
            db.commit()

            text = OCRService.extract_text(
                document.storage_path
            )

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_OCR,
                status="completed",
                message="OCR processing completed.",
            )
            db.commit()

            # =============================================
            # STAGE 2: CLASSIFICATION
            # =============================================
            document.processing_stage = (
                PROCESSING_STAGE_CLASSIFICATION
            )
            db.commit()

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_CLASSIFICATION,
                status="processing",
                message="Document classification started.",
            )
            db.commit()

            document_type = DocumentClassifier.classify(text)

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_CLASSIFICATION,
                status="completed",
                message="Document classification completed.",
            )
            db.commit()

            # =============================================
            # STAGE 3: METADATA EXTRACTION
            # =============================================
            document.processing_stage = PROCESSING_STAGE_METADATA
            db.commit()

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_METADATA,
                status="processing",
                message="Metadata extraction started.",
            )
            db.commit()

            metadata = ExtractorManager.extract(text)

            DocumentMetadataService.save_metadata(
                db=db,
                document_id=document.id,
                metadata=metadata,
            )

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_METADATA,
                status="completed",
                message="Metadata extraction completed.",
            )
            db.commit()

            # =============================================
            # STAGE 4: EMBEDDINGS
            # =============================================
            document.processing_stage = (
                PROCESSING_STAGE_EMBEDDING
            )
            db.commit()

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_EMBEDDING,
                status="processing",
                message="Embedding generation started.",
            )
            db.commit()

            DocumentChunkService.create_chunks(
                db=db,
                document_id=document.id,
                text=text,
            )

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_EMBEDDING,
                status="completed",
                message="Embedding generation completed.",
            )
            db.commit()

            # =============================================
            # COMPLETED
            # =============================================
            document.status = DOCUMENT_STATUS_COMPLETED
            document.processing_stage = (
                PROCESSING_STAGE_COMPLETED
            )

            DocumentProcessingLogService.log(
                db=db,
                document_id=document.id,
                stage=PROCESSING_STAGE_COMPLETED,
                status="completed",
                message="Document processing completed successfully.",
            )

            db.commit()
            db.refresh(document)

            print(
                f"DOCUMENT PROCESSING COMPLETED: "
                f"{document_id}"
            )

            return {
                "document_id": document.id,
                "document_type": document_type,
                "metadata": metadata,
                "status": document.status,
                "processing_stage": document.processing_stage,
            }

        except Exception as e:
            db.rollback()

            document = DocumentRepository.get_by_id_and_user(
                db=db,
                document_id=document_id,
                user_id=user_id,
            )

            if document is not None:
                document.status = DOCUMENT_STATUS_FAILED
                document.processing_stage = PROCESSING_STAGE_FAILED

                DocumentProcessingLogService.log(
                    db=db,
                    document_id=document.id,
                    stage=document.processing_stage,
                    status="failed",
                    message="Document processing failed.",
                )

                db.commit()

            print(
                f"DOCUMENT PROCESSING FAILED: "
                f"{document_id} - {str(e)}"
            )

            raise DocumentProcessingError(
                f"Document processing failed: {str(e)}"
            )
            
        
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

        # 2. Mark as processing
        document.status = DOCUMENT_STATUS_PROCESSING
        db.commit()
        db.refresh(document)

        try:
            # 3. OCR
            text = OCRService.extract_text(
                document.storage_path
            )

            # 4. Classification
            document_type = DocumentClassifier.classify(text)

            # 5. Metadata extraction
            metadata = ExtractorManager.extract(text)

            # 6. Save metadata
            DocumentMetadataService.save_metadata(
                db=db,
                document_id=document.id,
                metadata=metadata,
            )

            # 7. Chunking + embeddings
            DocumentChunkService.create_chunks(
                db=db,
                document_id=document.id,
                text=text,
            )

            # 8. Mark as completed
            document.status = DOCUMENT_STATUS_COMPLETED
            db.commit()
            db.refresh(document)

            return {
                "document_id": document.id,
                "document_type": document_type,
                "metadata": metadata,
                "status": document.status,
            }

        except ValueError as e:
            db.rollback()

            document.status = DOCUMENT_STATUS_FAILED
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(e),
            )

        except Exception as e:
            db.rollback()

            document.status = DOCUMENT_STATUS_FAILED
            db.commit()

            print(f"DOCUMENT PROCESSING ERROR: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document processing failed.",
            )
                    
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
        
    @staticmethod
    def reprocess_document(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        # 1. Verify document ownership
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
            # 2. Delete old metadata
            DocumentMetadataRepository.delete_by_document_id(
                db=db,
                document_id=document_id,
            )

            # 3. Delete old chunks and embeddings
            DocumentChunkRepository.delete_by_document_id(
                db=db,
                document_id=document_id,
            )

            # 4. Reset processing status
            document.status = DOCUMENT_STATUS_PROCESSING
            document.processing_stage = PROCESSING_STAGE_OCR

            # Commit cleanup as one transaction
            db.commit()
            db.refresh(document)

            # 5. Re-run processing pipeline
            return DocumentService.process_document(
                db=db,
                document_id=document_id,
                user_id=user_id,
            )

        except HTTPException:
            raise

        except Exception as e:
            db.rollback()

            document.status = DOCUMENT_STATUS_FAILED
            document.processing_stage = PROCESSING_STAGE_FAILED
            db.commit()

            print(f"DOCUMENT REPROCESSING ERROR: {str(e)}")

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Document reprocessing failed.",
            )