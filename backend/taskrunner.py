# /workspaces/TaskRun/backend/taskrunner.py
import os
import sys
# Ensure stdout uses utf-8 encoding to support emojis
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# 🚀 关键：将任务目录添加到Python路径
tasks_dir = os.getenv('TASKS_DIR', '/workspaces/TaskRun/examleTask')
sys.path.insert(0, tasks_dir)  # 🎯 将任务目录添加到Python路径最前面！

print(f"📁 任务目录: {tasks_dir}")
print(f"🐍 Python路径: {sys.path[:3]}...")  # 显示前3个路径

from funboost import BoosterDiscovery, BoostersManager

def main():
    # 🚀 自动发现所有消费函数
    discovery = BoosterDiscovery(
        project_root_path=tasks_dir,  # 🎯 直接设置为任务目录
        booster_dirs=['.'],           # 🎯 扫描当前目录
        max_depth=3,                  # 扫描3层子目录
    )
    discovery.auto_discovery()
    
    # 📋 显示所有发现的队列
    all_queues = BoostersManager.get_all_queues()
    print(f"✅ 发现了 {len(all_queues)} 个队列: {all_queues}")
    
    # 🚀🚀🚀🚀 一次性启动所有消费函数，每个队列开4个进程！
    print("🔥 正在启动所有消费函数，每个队列4个进程...")
    BoostersManager.mp_consume_all(4)
    
    print("🎉 所有消费者已启动！按 Ctrl+C 退出")

if __name__ == '__main__':
    main()
