from datetime import datetime

from pydantic import BaseModel


class DocumentSearchResult(BaseModel):
    document_id: int
    original_filename: str
    file_type: str
    status: str
    key: str
    value: str
    created_at: datetime