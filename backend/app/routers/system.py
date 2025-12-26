from fastapi import APIRouter
from app.dependencies import success_response
router = APIRouter()

@router.get('/system/health')
async def health_check():
    """健康检查接口"""
    return success_response(data={"status": "healthy"})