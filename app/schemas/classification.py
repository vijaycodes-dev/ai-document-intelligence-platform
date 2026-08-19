from pydantic import BaseModel


class ClassificationResponse(BaseModel):
    document_id: int
    document_type: str