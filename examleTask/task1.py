from public import MyBoosterParams

import asyncio  
import time  
import random
import typing  

from funboost import boost, FunctionResultStatusPersistanceConfig, BoosterParams,BrokerEnum,ctrl_c_recv,ConcurrentModeEnum  
from funboost.contrib.save_function_result_status.save_result_status_to_sqldb import save_result_status_to_sqlalchemy

@boost(MyBoosterParams(queue_name='每日任务',qps=0.00000005,  
max_retry_times=0,))  
def every_day(x,y:int=10):  
    time.sleep(2)  
    print(f'hello: {x} {y}')  
    if random.random() > 0.5:  
        raise ValueError('f2 error')  
    return x + y  