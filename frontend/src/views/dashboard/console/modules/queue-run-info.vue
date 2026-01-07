
<template>
  <div class="funboost-dashboard bg-gray-50 p-4 md:p-5 overflow-y-auto">
    <!-- 2. 操作栏 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 bg-white p-3 gap-4">
      <div class="flex flex-col sm:flex-row items-start sm:items-center gap-8 w-full sm:w-auto">
        <ElInput v-model="filterText" placeholder="搜索队列名或项目名..." class="w-full sm:w-72" clearable>
          <template #prefix><ElIcon><Search /></ElIcon></template>
        </ElInput>
        <ElSelect v-model="projectFilter" placeholder="筛选项目" clearable class="w-full sm:w-36">
          <ElOption v-for="p in uniqueProjects" :key="p" :label="p" :value="p" />
        </ElSelect>
      </div>
      <div class="flex gap-2 w-full sm:w-auto justify-end">
        <ElButton :icon="Refresh" @click="refreshData" :loading="loading">刷新看板</ElButton>
      </div>
    </div>
    <!-- 1. 全局统计看板：聚合所有队列的数据 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
    <ElCard  class="art-table-card" shadow="never">
        <div class="stats-label text-gray-500">总队列数</div>
        <div class="stats-value text-2xl font-bold">
          {{ Object.keys(allQueuesData).length }}
        </div>
      </ElCard>
    <ElCard  class="art-table-card" shadow="never">
        <div class="stats-label text-gray-500">待处理任务 (消息积压)</div>
        <div class="stats-value text-2xl font-bold text-orange-600">{{ globalStats.totalBacklog }}</div>
      </ElCard>
    <ElCard class="art-table-card" shadow="never">
        <div class="stats-label text-gray-500">当前活跃消费者进程</div>
        <div class="stats-value text-2xl font-bold text-green-600">{{ globalStats.totalConsumers }}</div>
      </ElCard>
    <ElCard class="art-table-card" shadow="never">
      <div class="stats-label text-gray-500">实时吞吐 (近10s)</div>
        <div class="stats-value text-2xl font-bold text-purple-600">
          {{ globalStats.totalThroughput }} <span class="text-sm font-normal">tasks/10s</span>
        </div>
      </ElCard>
    </div>





    <!-- 3. 队列卡片列表 -->
    <div v-loading="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <ElCard v-for="row in filteredQueues" :key="row.queue_name" shadow="hover" class="art-table-card">
        <template #header>
          <div class="flex justify-between items-center">
            <div>
              <div class="font-bold text-blue-600 text-lg">{{ row.queue_params.queue_name }}</div>
              <div class="text-sm text-gray-500">项目: {{ row.queue_params.project_name || '默认' }}</div>
            </div>
            <ElTag :type="row.pause_flag === 1 ? 'warning' : 'success'">
              {{ row.pause_flag === 1 ? '已暂停' : '消费中' }}
            </ElTag>
          </div>
        </template>

        <div class="space-y-3">
          <!-- 基本信息 -->
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="font-medium">中间件:</span> <ElTag effect="plain" size="small">{{ row.queue_params.broker_kind }}</ElTag></div>
            <div><span class="font-medium">消息积压:</span> <span :class="row.msg_num_in_broker > 1000 ? 'text-red-500 font-bold' : ''">{{ row.msg_num_in_broker }}</span></div>
          </div>

          <!-- 吞吐量 -->
          <div class="text-sm">
            <span class="font-medium">实时吞吐量 (10s):</span>
            <div class="mt-1">
              <span class="text-green-600 font-mono">{{ row.all_consumers_last_x_s_execute_count }} OK</span> /
              <span class="text-red-500 font-mono">{{ row.all_consumers_last_x_s_execute_count_fail }} ERR</span>
            </div>
          </div>

          <!-- 处理效能 -->
          <div class="text-sm">
            <span class="font-medium">处理效能:</span>
            <div class="mt-1 space-y-1">
              <div>均耗: <b class="text-purple-600">{{ row.all_consumers_avarage_function_spend_time_from_start || '-' }}s</b></div>
              <div>并发: <b>{{ row.queue_params.concurrent_num }}</b> ({{ row.queue_params.concurrent_mode }})</div>
            </div>
          </div>

          <!-- 历史统计 -->
          <div class="text-sm">
            <span class="font-medium">历史统计:</span>
            <div class="mt-1">
              总次数: <b>{{ row.all_consumers_total_consume_count_from_start }}</b><br/>
              失败率: <b :class="getFailRate(row) > 10 ? 'text-red-500' : ''">{{ getFailRate(row) }}%</b>
            </div>
          </div>

          <!-- 活跃消费者 -->
          <ElCollapse v-if="row.active_consumers.length > 0" class="mt-3">
            <ElCollapseItem title="活跃消费者实例" :name="'consumers-' + row.queue_name">
              <div class="space-y-2">
                <div v-for="consumer in row.active_consumers" :key="consumer.process_id" class="p-2 bg-gray-50 rounded text-xs">
                  <div class="grid grid-cols-2 gap-2">
                    <div><b>IP:</b> {{ consumer.computer_ip }}</div>
                    <div><b>PID:</b> {{ consumer.process_id }}</div>
                    <div><b>总成功:</b> {{ consumer.total_consume_count_from_start-consumer.total_consume_count_from_start_fail }}</div>
                    <div><b>总失败:</b> {{ consumer.total_consume_count_from_start_fail }}</div>
                    <div><b>耗时:</b> {{ consumer.total_cost_time_from_start }}s</div>
                    <div><b>启动:</b> {{ consumer.start_datetime_str }}</div>
                    <div class="col-span-2"><b>心跳:</b> <ElTag size="small" :type="isHeartbeatActive(consumer.hearbeat_timestamp) ? 'success' : 'danger'">{{ formatHeartbeat(consumer.hearbeat_timestamp) }}</ElTag></div>
                  </div>
                </div>
              </div>
            </ElCollapseItem>
          </ElCollapse>

          <!-- 操作按钮 -->
          <div class="flex gap-2 pt-2">
            <ElButton type="primary" @click="showConfig(row)">配置</ElButton>
            <ElButton 
              v-if="row.pause_flag === 0||row.pause_flag === -1" 
              type="warning" 
              @click="controlQueue(row.queue_params.queue_name, 'pause_consume')"
            >暂停</ElButton>
            <ElButton 
              v-else 
              type="success" 
              @click="controlQueue(row.queue_params.queue_name, 'resume_consume')"
            >恢复</ElButton>
            <ElPopconfirm title="确定清空队列积压消息吗？" @confirm="controlQueue(row.queue_params.queue_name, 'clear_queue')">
              <template #reference>
                <ElButton type="danger">清空</ElButton>
              </template>
            </ElPopconfirm>
          </div>
        </div>
      </ElCard>
    </div>


    <!-- 4. 配置详情弹窗 -->
    <ElDialog v-model="configDialogVisible" :title="'队列配置: ' + selectedQueueName" width="90%" class="max-w-4xl rounded-xl">
      <div v-if="selectedConfig" class="config-container">
        <div class="mb-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="config-item"><span class="label font-bold text-gray-600 mr-2">QPS限制:</span> {{ selectedConfig.qps || '无限制' }}</div>
          <div class="config-item"><span class="label font-bold text-gray-600 mr-2">最大重试:</span> {{ selectedConfig.max_retry_times }}</div>
          <div class="config-item"><span class="label font-bold text-gray-600 mr-2">RPC模式:</span> {{ selectedConfig.is_using_rpc_mode ? '开启' : '关闭' }}</div>
          <div class="config-item"><span class="label font-bold text-gray-600 mr-2">过滤去重:</span> {{ selectedConfig.do_task_filtering ? '开启' : '关闭' }}</div>
        </div>
        <ElDivider content-position="left">函数入参 Schema</ElDivider>
        <pre class="json-block bg-gray-800 text-gray-300 p-4 rounded overflow-auto max-h-80 font-mono text-sm leading-relaxed">{{ formatJson(selectedConfig.auto_generate_info.final_func_input_params_info) }}</pre>
        <ElDivider content-position="left">完整 BoosterParams</ElDivider>
        <pre class="json-block bg-gray-800 text-gray-300 p-4 rounded overflow-auto max-h-80 font-mono text-sm leading-relaxed">{{ formatJson(selectedConfig) }}</pre>
      </div>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { Search, Refresh, Setting, VideoPause, VideoPlay, Delete } from '@element-plus/icons-vue'
import { fetchGetAllQueueRunInfo, fetchPauseConsume, fetchResumeConsume, fetchClearQueue } from '@/api/funboost'
import { ElMessage, ElCollapse, ElCollapseItem, ElCard, ElButton, ElTag, ElPopconfirm, ElInput, ElSelect, ElOption, ElDivider } from 'element-plus'

// --- 数据定义 ---
const loading = ref(false)
const allQueuesData = ref<Record<string, any>>({})
const filterText = ref('')
const projectFilter = ref('')
const configDialogVisible = ref(false)
const selectedConfig = ref<any>(null)
const selectedQueueName = ref('')

// --- 逻辑处理 ---

// 获取全量运行信息
const refreshData = async () => {
  loading.value = true
  try {
    const res = await fetchGetAllQueueRunInfo()
    allQueuesData.value = res.queues
  } catch (err) {
    ElMessage.error('获取监控数据失败')
  } finally {
    loading.value = false
  }
}

// 筛选逻辑
const filteredQueues = computed(() => {
  const list = Object.values(allQueuesData.value)
  return list.filter(q => {
    const matchText = q.queue_params.queue_name.toLowerCase().includes(filterText.value.toLowerCase()) || 
                      (q.queue_params.project_name || '').toLowerCase().includes(filterText.value.toLowerCase())
    const matchProject = !projectFilter.value || q.queue_params.project_name === projectFilter.value
    return matchText && matchProject
  })
})

// 项目列表
const uniqueProjects = computed(() => {
  const projects = Object.values(allQueuesData.value).map(q => q.queue_params.project_name).filter(p => !!p)
  return [...new Set(projects)] as string[]
})

// 全局统计计算
const globalStats = computed(() => {
  const list = Object.values(allQueuesData.value)
  return {
    totalBacklog: list.reduce((sum, q) => sum + (q.msg_num_in_broker || 0), 0),
    totalConsumers: list.reduce((sum, q) => sum + q.active_consumers.length, 0),
    totalThroughput: list.reduce((sum, q) => sum + (q.all_consumers_last_x_s_execute_count || 0), 0)
  }
})

// 辅助工具
const getFailRate = (row: any) => {
  if (!row.all_consumers_total_consume_count_from_start) return 0
  return ((row.all_consumers_total_consume_count_from_start_fail / row.all_consumers_total_consume_count_from_start) * 100)
}

const isHeartbeatActive = (ts: number) => {
  return (Date.now() / 1000) - ts < 30
}

const formatHeartbeat = (ts: number) => {
  const diff = Math.floor((Date.now() / 1000) - ts)
  return diff < 5 ? '实时' : `${diff}s前`
}

const formatJson = (obj: any) => JSON.stringify(obj, null, 2)

// 队列控制动作
const controlQueue = async (queueName: string, action: string) => {
  try {
    let res: any
    console.log(`队列名：${queueName}，动作：${action}`)
    if (action === 'pause_consume') res = await fetchPauseConsume({ queue_name: queueName })
    else if (action === 'resume_consume') res = await fetchResumeConsume({ queue_name: queueName })
    else if (action === 'clear_queue') res = await fetchClearQueue({ queue_name: queueName })
  
    ElMessage.success('操作成功')
    setTimeout(refreshData, 1000) // 延迟刷新以便后台更新状态
    
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

const showConfig = (row: any) => {
  selectedConfig.value = row.queue_params
  selectedQueueName.value = row.queue_params.queue_name
  configDialogVisible.value = true
}

onMounted(() => {
  refreshData()
})

</script>

<style>
.custom-table :deep(.el-table__expanded-cell) {
  padding: 0 !important;
}

.stat-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.stat-title {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #495057;
}
</style>

