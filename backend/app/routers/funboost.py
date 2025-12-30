from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models.funboost_result import FunboostConsumeResult
from app.responses.base_response import PaginatedResponse
from app.schemas.funboost_result import FunboostResult
from app.dependencies.auth import verify_token
from app.dependencies import success_response
from funboost.faas import fastapi_router as fb_router

router = APIRouter()
"""
Funboost Faas 相关接口路由
"""
router.include_router(fb_router, dependencies=[Depends(verify_token)])

@router.get("/funboost/results")
def get_funboost_results(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    task_id: Optional[str] = None,
    queue_name: Optional[str] = None,
    success: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    query = db.query(FunboostConsumeResult)
    if task_id:
        query = query.filter(FunboostConsumeResult.task_id == task_id)
    if queue_name:
        query = query.filter(FunboostConsumeResult.queue_name == queue_name)
    if success is not None:
        query = query.filter(FunboostConsumeResult.success == success)

    total = query.count()
    results = query.offset((page - 1) * size).limit(size).all()

    return success_response(data=PaginatedResponse(
        data=[FunboostResult.model_validate(result) for result in results],
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size
    ))