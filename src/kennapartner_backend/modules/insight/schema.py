from pydantic import BaseModel, Field
from typing import Optional, List, Annotated


class Author(BaseModel):
    full_name: str
    email: str


class InsightSchema(BaseModel):
    title: str
    content: str
    authors: Annotated[List[Author], Field(description="List of authors")]


class QueryParamsSchema(BaseModel):
    page: int = Field(1, gt=0, le=100)
    limit: int = Field(10, ge=0)
    year: Optional[str] = None
    query: Optional[str] = None
