from typing import Any, Optional, List
from pydantic import BaseModel
from app.schemas.funboost_result import FunboostResult


class BaseResponse(BaseModel):
    succ: bool
    msg: str
    data: Optional[Any] = None
    code: int


class PaginatedResponse(BaseModel):
    data: List[FunboostResult]
    total: int
    page: int
    size: int
    total_pages: int