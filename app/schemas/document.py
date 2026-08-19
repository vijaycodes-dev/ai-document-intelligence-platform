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
    
