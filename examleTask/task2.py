from public import MyBoosterParams

import asyncio  
import time  
import random
import typing  

from funboost import boost, FunctionResultStatusPersistanceConfig, BoosterParams,BrokerEnum,ctrl_c_recv,ConcurrentModeEnum,fct
from funboost.contrib.save_function_result_status.save_result_status_to_sqldb import save_result_status_to_sqlalchemy
from nb_log import get_logger

@boost(MyBoosterParams(queue_name='主要任务',qps=0.5,  
max_retry_times=0,))  
def main_task(x,y:int=10):  
    logger=get_logger(fct.task_id)
    time.sleep(2)  
    logger.info(f'hello222: {x} {y}')  
    for index in range(10):
        time.sleep(5) 
        logger.info(f'当前等待次数{index}')
    return x + y  