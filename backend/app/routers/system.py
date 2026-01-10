from fastapi import APIRouter, Depends
from app.dependencies import success_response, error_response
from app.dependencies.auth import verify_token, verify_token_query
from sse_starlette.sse import EventSourceResponse
import subprocess
import os
import threading
import asyncio
from typing import AsyncGenerator
from collections import defaultdict

router = APIRouter()

process_store = {}
logs_store = {'process': [], 'install': []}

# SSE日志流管理器
class LogStreamManager:
    def __init__(self):
        self.subscribers: dict[str, dict[str, asyncio.Queue]] = defaultdict(dict)
        self._lock = threading.Lock()
    
    async def subscribe(self, log_type: str) -> AsyncGenerator:
        """订阅指定类型的日志流"""
        queue = asyncio.Queue()
        subscriber_id = str(id(queue))
        
        with self._lock:
            self.subscribers[log_type][subscriber_id] = queue
        
        try:
            # 先发送历史日志
            for log_line in logs_store.get(log_type, []):
                yield {"data": log_line}
            
            # 然后持续发送新日志
            while True:
                log_line = await queue.get()
                yield {"data": log_line}
        finally:
            with self._lock:
                if subscriber_id in self.subscribers[log_type]:
                    del self.subscribers[log_type][subscriber_id]
    
    def broadcast(self, log_type: str, log_line: str):
        """广播日志到所有订阅者"""
        with self._lock:
            for queue in self.subscribers[log_type].values():
                try:
                    # 使用 call_soon_threadsafe 从其他线程安全地添加到队列
                    queue._loop.call_soon_threadsafe(queue.put_nowait, log_line)
                except Exception:
                    pass

log_stream_manager = LogStreamManager()

def add_log(log_type, line):
    logs = logs_store[log_type]
    logs.append(line)
    if len(logs) > 500:
        logs.pop(0)
    # 广播到SSE订阅者
    log_stream_manager.broadcast(log_type, line)

def read_output(pipe, log_type):
    for line in iter(pipe.readline, ''):
        add_log(log_type, line.strip())

def install_requirements_if_exists(tasks_dir):
    """使用Popen实时捕获pip install输出"""
    req_file = os.path.join(tasks_dir, 'requirements.txt')
    if os.path.exists(req_file):
        try:
            # 使用Popen替代run以实时捕获输出
            process = subprocess.Popen(
                ['pip', 'install', '-r', 'requirements.txt'],
                cwd=tasks_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                text=True,
                bufsize=1  # 行缓冲
            )
            
            # 实时读取输出
            for line in iter(process.stdout.readline, ''):
                if line:
                    add_log('install', line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception(f"安装依赖失败，退出码: {process.returncode}")
            
            return True
        except Exception as e:
            error_msg = f"安装依赖失败: {str(e)}"
            add_log('install', error_msg)
            raise Exception(error_msg)
    return False

@router.get('/system/health')
async def health_check():
    """健康检查接口"""
    return success_response(data={"status": "healthy"})

@router.post("/process/install", dependencies=[Depends(verify_token)])
async def install_dependencies():
    """
    安装依赖接口
    """
    tasks_dir = os.getenv('TASKS_DIR', '/workspaces/TaskRun/examleTask')
    
    def install():
        try:
            install_requirements_if_exists(tasks_dir)
        except Exception as e:
            # 错误已在 install_requirements_if_exists 中记录到日志
            pass
    
    threading.Thread(target=install).start()
    return success_response(msg="依赖安装已开始")

@router.post("/process/start", dependencies=[Depends(verify_token)])
async def start_process():
    """
    启动子进程接口
    """
    if 'taskrunner' in process_store and process_store['taskrunner'].poll() is None:
        return error_response(msg="进程已在运行")
    
    try:
        process_store['taskrunner'] = subprocess.Popen(['python', 'taskrunner.py'], cwd=os.path.dirname(__file__) + '/../..', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=read_output, args=(process_store['taskrunner'].stdout, 'process')).start()
        threading.Thread(target=read_output, args=(process_store['taskrunner'].stderr, 'process')).start()
        return success_response(msg="进程启动成功")
    except Exception as e:
        return error_response(msg=f"启动失败: {str(e)}")

@router.post("/process/restart", dependencies=[Depends(verify_token)])
async def restart_process():
    """
    重启子进程接口
    """
    try:
        # 先停止所有相关的 taskrunner 进程
        result = subprocess.run(['pkill', '-f', 'taskrunner.py'], capture_output=True, text=True)
        
        # 清理存储的进程引用
        if 'taskrunner' in process_store:
            del process_store['taskrunner']
        
        # 再启动
        process_store['taskrunner'] = subprocess.Popen(['python', 'taskrunner.py'], cwd=os.path.dirname(__file__) + '/../..', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=read_output, args=(process_store['taskrunner'].stdout, 'process')).start()
        threading.Thread(target=read_output, args=(process_store['taskrunner'].stderr, 'process')).start()
        return success_response(msg="进程重启成功")
    except Exception as e:
        return error_response(msg=f"重启失败: {str(e)}")

@router.post("/process/stop", dependencies=[Depends(verify_token)])
async def stop_process():
    """
    终止子进程接口
    """
    try:
        # 使用 pkill 终止所有 taskrunner.py 进程
        result = subprocess.run(['pkill', '-f', 'taskrunner.py'], capture_output=True, text=True)
        
        # 清理存储的进程引用
        if 'taskrunner' in process_store:
            del process_store['taskrunner']
        
        if result.returncode == 0 or result.returncode == 1:  # 0 表示找到并终止，1 表示未找到
            return success_response(msg="进程终止成功")
        else:
            return error_response(msg=f"终止失败: {result.stderr}")
    except Exception as e:
        return error_response(msg=f"终止失败: {str(e)}")

@router.get("/process/status", dependencies=[Depends(verify_token)])
async def get_process_status():
    """
    查询子进程状态接口
    """
    if 'taskrunner' in process_store and process_store['taskrunner'].poll() is None:
        return success_response(data={"status": "running", "pid": process_store['taskrunner'].pid})
    else:
        return success_response(data={"status": "stopped"})

@router.get('/logs', dependencies=[Depends(verify_token)])
async def get_process_logs():
    """
    查看子进程日志接口（备用接口，保留兼容性）
    """
    return success_response(data={'logs': logs_store['process']})

@router.get('/install/logs', dependencies=[Depends(verify_token)])
async def get_install_logs():
    """
    查看安装日志接口（备用接口，保留兼容性）
    """
    return success_response(data={'logs': logs_store['install']})

@router.get('/logs/stream')
async def stream_process_logs(_: str = Depends(verify_token_query)):
    """
    SSE实时进程日志流
    """
    return EventSourceResponse(log_stream_manager.subscribe('process'))

@router.get('/install/logs/stream')
async def stream_install_logs(_: str = Depends(verify_token_query)):
    """
    SSE实时安装日志流
    """
    return EventSourceResponse(log_stream_manager.subscribe('install'))