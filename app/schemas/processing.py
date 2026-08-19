from pydantic import BaseModel


class ProcessingResponse(BaseModel):
    document_id: int
    document_type: str
    metadata: dict