from fastapi import APIRouter, Depends
from app.models.user import LoginRequest, UserInfo
from app.dependencies.auth import create_access_token, verify_token
from app.dependencies import success_response, error_response
import os

router = APIRouter()

@router.post("/auth/login")
async def login(request: LoginRequest):
    """
    用户登录接口
    
    :param request: 说明
    :type request: LoginRequest
    """
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    if request.username == admin_username and request.password == admin_password:
        access_token = create_access_token(data={"sub": request.username})
        return success_response(
            msg="登录成功",
            data={
                "token": access_token,
                "token_type": "bearer"
            }
        )
    else:
        return error_response(msg="用户名或密码错误")

@router.get("/user/info", dependencies=[Depends(verify_token)])
async def get_user_info():
    """
    获取用户信息接口
    """
    user_info = UserInfo(
        buttons=["add", "edit", "delete"],
        roles=["R_SUPER"],
        userId=1,
        username="admin",
        email="admin@example.com",
        avatar=None
    )
    return success_response(data=user_info.dict())