"""
Pagination schemas
Generic pagination response for list endpoints
"""

from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T] = Field(..., description="List of items in current page")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")

    class Config:
        from_attributes = True
