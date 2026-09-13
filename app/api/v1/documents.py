from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.classification import ClassificationResponse
from app.schemas.document import (
    DocumentResponse,
    PaginatedDocumentResponse,
    ProcessingLogResponse,
)
from app.schemas.document_search import DocumentSearchResult
from app.schemas.ocr import OCRResponse
from app.schemas.processing import ProcessingResponse
from app.schemas.semantic_search import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.schemas.summary import SummaryResponse

from app.services.document_metadata_service import (
    DocumentMetadataService,
)
from app.services.document_service import DocumentService
from app.services.semantic_search_service import (
    SemanticSearchService,
)

from app.repositories.document_repository import DocumentRepository

from app.schemas.question_answer import (
    AskQuestionRequest,
    AskQuestionResponse,
)
from app.services.question_answer_service import (
    QuestionAnswerService,
)
from app.tasks.document_tasks import process_document_task

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# =========================================================
# DOCUMENT COLLECTION
# =========================================================

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


@router.get(
    "",
    response_model=PaginatedDocumentResponse,
)
def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    file_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.list_documents(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
        file_type=file_type,
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
        user_id=current_user.id,
        document_id=request.document_id,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "results": [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "similarity": round(1 - distance, 4),
                "text": chunk.chunk_text,
            }
            for chunk, distance in results
        ],
    }

@router.post(
    "/ask",
    response_model=AskQuestionResponse,
)
def ask_question(
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return QuestionAnswerService.ask(
        db=db,
        question=request.question,
        user_id=current_user.id,
        document_id=request.document_id,
        limit=request.limit,
    )
    
# =========================================================
# INDIVIDUAL DOCUMENT
# =========================================================

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

    
# =========================================================
# DELETE DOCUMENT
# =========================================================

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
    
    
    
#----------------------------------------------------------
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
    status_code=status.HTTP_202_ACCEPTED,
)
def process_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = DocumentService.mark_document_processing(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    background_tasks.add_task(
        process_document_task,
        document_id=document.id,
        user_id=current_user.id,
    )

    return {
        "document_id": document.id,
        "status": document.status,
        "message": "Document processing started.",
    }
    
    

@router.get(
    "/{document_id}/status",
)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    return {
        "document_id": document.id,
        "status": document.status,
        "processing_stage": document.processing_stage,
    }
    
@router.get(
    "/{document_id}/processing-history",
    response_model=list[ProcessingLogResponse],
)
def get_processing_history(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.get_processing_history(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )
    
    

@router.post(
    "/{document_id}/reprocess",
    response_model=ProcessingResponse,
)
def reprocess_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService.reprocess_document(
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

