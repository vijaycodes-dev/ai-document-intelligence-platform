from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str
    document_id: int | None = None
    limit: int = 5


class SemanticSearchResult(BaseModel):
    document_id: int
    chunk_index: int
    similarity: float
    text: str


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]