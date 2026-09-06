from pydantic import BaseModel, Field, field_validator


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    document_id: int | None = None
    limit: int = Field(default=5, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value


class SourceChunk(BaseModel):
    document_id: int
    chunk_index: int
    similarity: float
    text: str


class AskQuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]