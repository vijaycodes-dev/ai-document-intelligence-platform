from pydantic import BaseModel, Field, field_validator


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: int | None = None
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Search query cannot be empty.")

        return value


class SemanticSearchResult(BaseModel):
    document_id: int
    chunk_index: int
    similarity: float
    text: str


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]
