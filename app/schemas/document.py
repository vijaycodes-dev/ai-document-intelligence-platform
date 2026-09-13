    
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    uploaded_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ProcessingLogResponse(BaseModel):
    id: int
    document_id: int
    stage: str
    status: str
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocumentResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
