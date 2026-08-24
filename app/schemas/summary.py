from pydantic import BaseModel


class SummaryResponse(BaseModel):
    document_id: int
    summary: str