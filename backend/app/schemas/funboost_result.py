from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class FunboostResult(BaseModel):
    _id: str
    function: Optional[str]
    host_name: Optional[str]
    host_process: Optional[str]
    insert_minutes: Optional[str]
    insert_time: Optional[datetime]
    insert_time_str: Optional[str]
    publish_time: Optional[float]
    publish_time_format: Optional[str]
    msg_dict: Optional[Any]
    params: Optional[Any]
    params_str: Optional[str]
    process_id: Optional[int]
    queue_name: Optional[str]
    result: Optional[str]
    run_times: Optional[int]
    script_name: Optional[str]
    script_name_long: Optional[str]
    success: Optional[bool]
    task_id: Optional[str]
    thread_id: Optional[int]
    time_cost: Optional[float]
    time_end: Optional[float]
    time_start: Optional[float]
    total_thread: Optional[int]
    utime: Optional[str]
    exception: Optional[str]
    rpc_result_expire_seconds: Optional[int]
    exception_type: Optional[str]
    exception_msg: Optional[str]
    rpc_chain_error_msg_dict: Optional[str]
    run_status: Optional[str]

    class Config:
        from_attributes = True