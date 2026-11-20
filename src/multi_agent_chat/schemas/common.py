from pydantic import BaseModel, Field, field_validator


class PaginationParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class PartialUpdate(BaseModel):
    """Allow omitted fields, but reject null for non-nullable columns."""

    @field_validator('*', check_fields=False)
    @classmethod
    def field_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Field cannot be null')
        return value
