from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.dependencies import success_response, error_response
from app.dependencies.auth import verify_token
import os
import json
from pathlib import Path

router = APIRouter()

# 获取TASKS_DIR路径，默认为examleTask目录
TASKS_DIR = os.getenv('TASKS_DIR', '/workspaces/TaskRun/examleTask')

# Pydantic 模型
class WriteFileRequest(BaseModel):
    path: str
    content: str

class DeleteFileRequest(BaseModel):
    path: str

class CreateFileRequest(BaseModel):
    path: str
    is_dir: bool = False

def validate_path(file_path: str) -> str:
    """验证文件路径，防止目录遍历攻击"""
    # 规范化路径
    full_path = os.path.normpath(os.path.join(TASKS_DIR, file_path))
    
    # 确保路径在TASKS_DIR下
    if not full_path.startswith(os.path.normpath(TASKS_DIR)):
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    return full_path


@router.get("/files/list", dependencies=[Depends(verify_token)])
async def list_files(path: str = "/"):
    """
    列出目录下的所有文件和目录
    
    Args:
        path: 相对于TASKS_DIR的路径，为 "/" 或空时列出根目录
    
    Returns:
        包含文件和目录列表的响应
    """
    try:
        # 处理根路径
        if path == "/" or path == "":
            path = ""
        
        full_path = validate_path(path)
        
        if not os.path.exists(full_path):
            return error_response(msg="路径不存在")
        
        if not os.path.isdir(full_path):
            return error_response(msg="路径不是目录")
        
        items = []
        try:
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                is_dir = os.path.isdir(item_path)
                items.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "path": os.path.relpath(item_path, TASKS_DIR).replace("\\", "/"),
                    "is_dir": is_dir,
                    "size": os.path.getsize(item_path) if not is_dir else None,
                    "mtime": os.path.getmtime(item_path)
                })
        except PermissionError:
            return error_response(msg="没有读取权限")
        
        # 按照目录优先，然后按名称排序
        items.sort(key=lambda x: (not x['is_dir'], x['name']))
        
        return success_response(data={"items": items, "path": path or "/"})
    
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(msg=f"读取目录失败: {str(e)}")


@router.get("/files/read", dependencies=[Depends(verify_token)])
async def read_file(path: str):
    """
    读取文件内容
    
    Args:
        path: 相对于TASKS_DIR的文件路径
    
    Returns:
        文件内容
    """
    try:
        full_path = validate_path(path)
        
        if not os.path.exists(full_path):
            return error_response(msg="文件不存在")
        
        if not os.path.isfile(full_path):
            return error_response(msg="路径不是文件")
        
        # 检查文件大小，限制在10MB以内
        file_size = os.path.getsize(full_path)
        if file_size > 10 * 1024 * 1024:
            return error_response(msg="文件过大，不能超过10MB")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return success_response(data={
                "path": path,
                "content": content,
                "size": file_size,
                "name": os.path.basename(full_path)
            })
        except UnicodeDecodeError:
            return error_response(msg="文件不是有效的UTF-8文本文件")
    
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(msg=f"读取文件失败: {str(e)}")


@router.post("/files/write", dependencies=[Depends(verify_token)])
async def write_file(request: WriteFileRequest):
    """
    写入文件内容
    
    Args:
        request: 包含path和content的请求体
    
    Returns:
        写入结果
    """
    try:
        full_path = validate_path(request.path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(request.content)
            
            return success_response(data={
                "path": request.path,
                "size": len(request.content.encode('utf-8')),
                "message": "文件已保存"
            }, msg="文件保存成功")
        except Exception as write_error:
            return error_response(msg=f"写入文件失败: {str(write_error)}")
    
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(msg=f"保存文件失败: {str(e)}")


@router.delete("/files/delete", dependencies=[Depends(verify_token)])
async def delete_file(request: DeleteFileRequest):
    """
    删除文件或目录
    
    Args:
        request: 包含path的请求体
    
    Returns:
        删除结果
    """
    try:
        full_path = validate_path(request.path)
        
        if not os.path.exists(full_path):
            return error_response(msg="文件或目录不存在")
        
        try:
            if os.path.isdir(full_path):
                import shutil
                shutil.rmtree(full_path)
                msg = "目录已删除"
            else:
                os.remove(full_path)
                msg = "文件已删除"
            
            return success_response(msg=msg)
        except Exception as delete_error:
            return error_response(msg=f"删除失败: {str(delete_error)}")
    
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(msg=f"删除失败: {str(e)}")


@router.post("/files/create", dependencies=[Depends(verify_token)])
async def create_file_or_dir(request: CreateFileRequest):
    """
    创建文件或目录
    
    Args:
        request: 包含path和is_dir的请求体
    
    Returns:
        创建结果
    """
    try:
        full_path = validate_path(request.path)
        
        if os.path.exists(full_path):
            return error_response(msg="文件或目录已存在")
        
        try:
            if request.is_dir:
                os.makedirs(full_path, exist_ok=True)
                msg = "目录已创建"
            else:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                open(full_path, 'a').close()
                msg = "文件已创建"
            
            return success_response(msg=msg)
        except Exception as create_error:
            return error_response(msg=f"创建失败: {str(create_error)}")
    
    except Exception as e:
        return error_response(msg=f"创建失败: {str(e)}")


class RenameFileRequest(BaseModel):
    old_path: str
    new_path: str


@router.post("/files/rename", dependencies=[Depends(verify_token)])
async def rename_file(request: RenameFileRequest):
    """
    重命名或移动文件/目录
    
    Args:
        request: 包含old_path和new_path的请求体
    
    Returns:
        操作结果
    """
    try:
        old_full_path = validate_path(request.old_path)
        # 验证新路径，确保也在TASKS_DIR下
        new_full_path = validate_path(request.new_path)
        
        if not os.path.exists(old_full_path):
            return error_response(msg="原文件或目录不存在")
        
        if os.path.exists(new_full_path):
            return error_response(msg="目标路径已存在")
            
        # 确保目标目录存在
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        
        try:
            os.rename(old_full_path, new_full_path)
            return success_response(msg="操作成功")
        except Exception as rename_error:
            return error_response(msg=f"操作失败: {str(rename_error)}")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        return error_response(msg=f"操作失败: {str(e)}")
