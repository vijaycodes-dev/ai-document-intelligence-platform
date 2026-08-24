from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from fastapi.responses import FileResponse
from app.schemas.ocr import OCRResponse
from app.schemas.classification import ClassificationResponse
from app.schemas.processing import ProcessingResponse
from app.services.document_metadata_service import DocumentMetadataService
from app.repositories.document_repository import DocumentRepository
from fastapi import HTTPException, status
from app.schemas.document_search import DocumentSearchResult
from app.schemas.summary import SummaryResponse

from app.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.services.semantic_search_service import (
    SemanticSearchService,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.upload_document(
        db=db,
        file=file,
        user_id=current_user.id,
    )
    
from typing import List

@router.get(
    "",
    response_model=List[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.list_documents(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/search",
    response_model=list[DocumentSearchResult],
)
def search_documents(
    key: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = DocumentMetadataService.search_metadata(
        db=db,
        key=key,
        value=value,
        user_id=current_user.id,
    )

    return [
        DocumentSearchResult(
            document_id=metadata.document_id,
            original_filename=document.original_filename,
            file_type=document.file_type,
            status=document.status,
            key=metadata.key,
            value=metadata.value,
            created_at=document.created_at,
        )
        for metadata, document in results
    ]
    
@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    
@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    
@router.get(
    "/{document_id}/download",
)
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = DocumentService.download_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    return FileResponse(
        path=document.storage_path,
        filename=document.original_filename,
        media_type=document.file_type,
    )
    
@router.get(
    "/{document_id}/ocr",
    response_model=OCRResponse,
)
def extract_text(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.extract_document_text(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    
@router.get(
    "/{document_id}/classify",
    response_model=ClassificationResponse,
)
def classify_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.classify_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

@router.post(
    "/{document_id}/process",
    response_model=ProcessingResponse,
)
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.process_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

@router.get(
    "/{document_id}/metadata",
)
def get_document_metadata(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = DocumentRepository.get_by_id_and_user(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    metadata = DocumentMetadataService.get_metadata(
        db=db,
        document_id=document_id,
    )

    return {
        "document_id": document_id,
        "metadata": [
            {
                "key": item.key,
                "value": item.value,
            }
            for item in metadata
        ],
    }
    
@router.get(
    "/{document_id}/summary",
    response_model=SummaryResponse,
)
def summarize_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.summarize_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    
    
@router.post(
    "/semantic-search",
    response_model=SemanticSearchResponse,
)
def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = SemanticSearchService.search(
        db=db,
        query=request.query,
        document_id=request.document_id,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "results": [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "similarity": 1 - distance,
                "text": chunk.chunk_text,
            }
            for chunk, distance in results
        ],
    }