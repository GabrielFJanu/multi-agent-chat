from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)
