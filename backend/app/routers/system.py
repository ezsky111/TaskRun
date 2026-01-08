from fastapi import APIRouter, Depends, BackgroundTasks
from app.dependencies import success_response, error_response
from app.dependencies.auth import verify_token
import subprocess
import os
import asyncio
from collections import deque

router = APIRouter()

process_store = {}
logs = deque(maxlen=500)

async def install_requirements_if_exists(tasks_dir, logs):
    req_file = os.path.join(tasks_dir, 'requirements.txt')
    if os.path.exists(req_file):
        try:
            process = await asyncio.create_subprocess_exec(
                'pip', 'install', '-r', 'requirements.txt',
                cwd=tasks_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if stdout:
                logs.append(f"Install stdout: {stdout.decode().strip()}")
            if stderr:
                logs.append(f"Install stderr: {stderr.decode().strip()}")
            if process.returncode != 0:
                raise Exception(f"安装依赖失败: {stderr.decode()}")
            return True
        except Exception as e:
            logs.append(f"Install error: {str(e)}")
            raise
    return False

async def start_background(tasks_dir, logs):
    try:
        await install_requirements_if_exists(tasks_dir, logs)
        process = await asyncio.create_subprocess_exec(
            'python', 'taskrunner.py',
            cwd=os.path.dirname(__file__) + '/../..',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        process_store['taskrunner'] = process

        async def read_output(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                logs.append(f"{prefix}: {line.decode().strip()}")

        await asyncio.gather(
            read_output(process.stdout, "TaskRunner stdout"),
            read_output(process.stderr, "TaskRunner stderr")
        )
    except Exception as e:
        logs.append(f"Start error: {str(e)}")

@router.get('/system/health')
async def health_check():
    """健康检查接口"""
    return success_response(data={"status": "healthy"})

@router.post("/process/start", dependencies=[Depends(verify_token)])
async def start_process(background_tasks: BackgroundTasks):
    """
    启动子进程接口
    """
    if 'taskrunner' in process_store and process_store['taskrunner'].returncode is None:
        return error_response(msg="进程已在运行")
    
    tasks_dir = os.getenv('TASKS_DIR', '/workspaces/TaskRun/examleTask')
    background_tasks.add_task(start_background, tasks_dir, logs)
    return success_response(msg="进程启动中")

@router.post("/process/restart", dependencies=[Depends(verify_token)])
async def restart_process(background_tasks: BackgroundTasks):
    """
    重启子进程接口
    """
    try:
        # 先停止
        if 'taskrunner' in process_store:
            process_store['taskrunner'].terminate()
            await process_store['taskrunner'].wait()
            del process_store['taskrunner']
        
        tasks_dir = os.getenv('TASKS_DIR', '/workspaces/TaskRun/examleTask')
        background_tasks.add_task(start_background, tasks_dir, logs)
        return success_response(msg="进程重启中")
    except Exception as e:
        return error_response(msg=f"重启失败: {str(e)}")

@router.post("/process/stop", dependencies=[Depends(verify_token)])
async def stop_process():
    """
    终止子进程接口
    """
    try:
        if 'taskrunner' in process_store:
            process_store['taskrunner'].terminate()
            await process_store['taskrunner'].wait()
            del process_store['taskrunner']
        return success_response(msg="进程终止成功")
    except Exception as e:
        return error_response(msg=f"终止失败: {str(e)}")

@router.get("/process/status", dependencies=[Depends(verify_token)])
async def get_process_status():
    """
    查询子进程状态接口
    """
    if 'taskrunner' in process_store and process_store['taskrunner'].returncode is None:
        return success_response(data={"status": "running", "pid": process_store['taskrunner'].pid})
    else:
        return success_response(data={"status": "stopped"})

@router.get("/logs", dependencies=[Depends(verify_token)])
async def get_logs():
    """
    查询日志接口
    """
    return success_response(data={"logs": list(logs)})