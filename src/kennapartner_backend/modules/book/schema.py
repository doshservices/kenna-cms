from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookSchema(BaseModel):
    name: str
    introduction: str
    preface: str
    foreword: str
    author: str
    date: datetime
    


class QueryParamsSchema(BaseModel):
    page: int = Field(1, gt=0, le=100)
    limit: int = Field(10, ge=0)
    year: Optional[str] = None
    query: Optional[str] = None
