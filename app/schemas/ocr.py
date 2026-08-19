from pydantic import BaseModel


class OCRResponse(BaseModel):
    document_id: int
    extracted_text: str