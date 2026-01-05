import asyncio  
import time  
import random  

from funboost import boost, FunctionResultStatusPersistanceConfig, BoosterParams,BrokerEnum,ctrl_c_recv,ConcurrentModeEnum  
from funboost.contrib.save_function_result_status.save_result_status_to_sqldb import save_result_status_to_sqlalchemy


class MyBoosterParams(BoosterParams):  
    project_name:str = '测试项目1'  # 核心配置，项目名，设置后，web接口就可以只关心某个项目下的队列，减少无关返回信息的干扰。
    broker_kind:str = BrokerEnum.REDIS
    is_send_consumer_hearbeat_to_redis : bool= True # 向redis发送心跳，这样才能从redis获取相关队列的运行信息。
    is_using_rpc_mode:bool = True # 必须设置这一个参数为True，才能支持rpc功能。
    booster_group : str = 'test_group1' # 方便按分组启动消费
    user_custom_record_process_info_func=save_result_status_to_sqlalchemy
    should_check_publish_func_params:bool = False # 发布消息时，是否检查消息内容是否正确，不正确的消息格式立刻从接口返回报错消息内容不正确。


@boost(MyBoosterParams(queue_name='测试中文通道',qps=1,))  
def f(x):  
    time.sleep(5)  
    print(f'hi: {x}')  
    return x + 1  

@boost(MyBoosterParams(queue_name='queue_test_g02t',qps=0.5,  
max_retry_times=0,))  
def f2(x,y):  
    time.sleep(2)  
    print(f'hello: {x} {y}')  
    if random.random() > 0.5:  
        raise ValueError('f2 error')  
    return x + y  


if __name__ == '__main__':      
    f.multi_process_consume(4)  
    f2.multi_process_consume(5)
    for _ in range(10):
        time.sleep(5)
        f.push(10)
        f2.push(20,30)
    ctrl_c_recv()  