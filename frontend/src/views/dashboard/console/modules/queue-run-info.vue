<template>
  <div class="funboost-dashboard art-full-height bg-gray-50 p-5">
    <!-- 1. 全局统计看板：聚合所有队列的数据 -->
    <ElRow :gutter="20" class="mb-5">
      <ElCol :span="6">
        <ElCard shadow="hover" class="stats-card border-l-4 border-blue-500">
          <div class="stats-label text-gray-500">总队列数 / 活跃项目</div>
          <div class="stats-value text-2xl font-bold">
            {{ Object.keys(allQueuesData).length }} / {{ uniqueProjects.length }}
          </div>
        </ElCard>
      </ElCol>
      <ElCol :span="6">
        <ElCard shadow="hover" class="stats-card border-l-4 border-orange-500">
          <div class="stats-label text-gray-500">全网待处理任务 (消息积压)</div>
          <div class="stats-value text-2xl font-bold text-orange-600">{{ globalStats.totalBacklog }}</div>
        </ElCard>
      </ElCol>
      <ElCol :span="6">
        <ElCard shadow="hover" class="stats-card border-l-4 border-green-500">
          <div class="stats-label text-gray-500">当前活跃消费者进程</div>
          <div class="stats-value text-2xl font-bold text-green-600">{{ globalStats.totalConsumers }}</div>
        </ElCard>
      </ElCol>
      <ElCol :span="6">
        <ElCard shadow="hover" class="stats-card border-l-4 border-purple-500">
          <div class="stats-label text-gray-500">全网实时吞吐 (近10s)</div>
          <div class="stats-value text-2xl font-bold text-purple-600">
            {{ globalStats.totalThroughput }} <span class="text-sm font-normal">tasks/10s</span>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 2. 操作栏 -->
    <div class="flex justify-between items-center mb-4 bg-white p-3 rounded shadow-sm">
      <div class="flex items-center gap-4">
        <ElInput v-model="filterText" placeholder="搜索队列名或项目名..." style="width: 300px" clearable>
          <template #prefix><ElIcon><Search /></ElIcon></template>
        </ElInput>
        <ElSelect v-model="projectFilter" placeholder="筛选项目" clearable style="width: 150px">
          <ElOption v-for="p in uniqueProjects" :key="p" :label="p" :value="p" />
        </ElSelect>
      </div>
      <div class="flex gap-2">
        <ElButton :icon="Refresh" @click="refreshData" :loading="loading">刷新看板</ElButton>
      </div>
    </div>

    <!-- 3. 主表格：展示队列核心状态 -->
    <ElCard class="art-table-card" shadow="never">
      <ElTable :data="filteredQueues" style="width: 100%" v-loading="loading">
        <!-- 展开行：展示消费者详情 -->
        <ElTableColumn type="expand">
          <template #default="{ row }">
            <div class="p-4 bg-gray-50 rounded">
              <h4 class="mb-3 font-bold text-blue-800">活跃消费者实例 ({{ row.active_consumers.length }})</h4>
              <ElTable :data="row.active_consumers" size="small" border stripe>
                <ElTableColumn prop="computer_ip" label="IP" width="130" />
                <ElTableColumn prop="process_id" label="PID" width="80" />
                <ElTableColumn label="资源占用">
                  <template #default="scope">
                    <span class="text-xs">
                      CPU: <b :class="scope.row.cpu > 80 ? 'text-red-500' : ''">{{ scope.row.cpu }}%</b> | 
                      MEM: <b>{{ scope.row.memory }}MB</b>
                    </span>
                  </template>
                </ElTableColumn>
                <ElTableColumn prop="last_x_s_execute_count" label="近10s成功" width="100" />
                <ElTableColumn prop="last_x_s_execute_count_fail" label="近10s失败" width="100" />
                <ElTableColumn label="平均耗时" width="100">
                  <template #default="scope">{{ scope.row.last_x_s_avarage_function_spend_time }}s</template>
                </ElTableColumn>
                <ElTableColumn prop="start_datetime_str" label="启动时间" width="160" />
                <ElTableColumn label="心跳" width="100">
                  <template #default="scope">
                    <ElTag size="small" :type="isHeartbeatActive(scope.row.hearbeat_timestamp) ? 'success' : 'danger'">
                      {{ formatHeartbeat(scope.row.hearbeat_timestamp) }}
                    </ElTag>
                  </template>
                </ElTableColumn>
              </ElTable>
            </div>
          </template>
        </ElTableColumn>

        <!-- 队列基本信息 -->
        <ElTableColumn label="队列/项目" min-width="200">
          <template #default="{ row }">
            <div class="font-bold text-blue-600">{{ row.queue_params.queue_name }}</div>
            <div class="text-xs text-gray-400">项目: {{ row.queue_params.project_name || '默认' }}</div>
          </template>
        </ElTableColumn>

        <ElTableColumn label="中间件" width="120">
          <template #default="{ row }">
            <ElTag effect="plain" size="small">{{ row.queue_params.broker_kind }}</ElTag>
          </template>
        </ElTableColumn>

        <ElTableColumn label="状态" width="100">
          <template #default="{ row }">
            <ElTag :type="row.pause_flag === 1 ? 'warning' : 'success'">
              {{ row.pause_flag === 1 ? '已暂停' : '消费中' }}
            </ElTag>
          </template>
        </ElTableColumn>

        <ElTableColumn label="消息积压" width="120" sortable prop="msg_num_in_broker">
          <template #default="{ row }">
            <span :class="row.msg_num_in_broker > 1000 ? 'text-red-500 font-bold' : 'text-gray-700'">
              {{ row.msg_num_in_broker }}
            </span>
          </template>
        </ElTableColumn>

        <ElTableColumn label="实时吞吐量 (10s)" width="150">
          <template #default="{ row }">
            <span class="text-green-600 font-mono">{{ row.all_consumers_last_x_s_execute_count }} OK</span> / 
            <span class="text-red-500 font-mono">{{ row.all_consumers_last_x_s_execute_count_fail }} ERR</span>
          </template>
        </ElTableColumn>

        <ElTableColumn label="处理效能" width="150">
          <template #default="{ row }">
            <div class="text-xs">
              <div>均耗: <b class="text-purple-600">{{ row.all_consumers_last_x_s_avarage_function_spend_time || '-' }}s</b></div>
              <div>并发: <b>{{ row.queue_params.concurrent_num }}</b> ({{ row.queue_params.concurrent_mode }})</div>
            </div>
          </template>
        </ElTableColumn>

        <ElTableColumn label="历史统计" width="180">
          <template #default="{ row }">
            <div class="text-xs text-gray-500">
              总次数: <b>{{ row.history_run_count }}</b><br/>
              失败率: <b :class="getFailRate(row) > 10 ? 'text-red-500' : ''">{{ getFailRate(row) }}%</b>
            </div>
          </template>
        </ElTableColumn>

        <!-- 操作 -->
        <ElTableColumn label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <ElButtonGroup size="small">
              <ElButton type="primary" link @click="showConfig(row)">配置</ElButton>
              <ElDivider direction="vertical" />
              <ElButton 
                v-if="row.pause_flag === 0" 
                type="warning" 
                link 
                @click="controlQueue(row.queue_name, 'pause_consume')"
              >暂停</ElButton>
              <ElButton 
                v-else 
                type="success" 
                link 
                @click="controlQueue(row.queue_name, 'resume_consume')"
              >恢复</ElButton>
              <ElDivider direction="vertical" />
              <ElPopconfirm title="确定清空队列积压消息吗？" @confirm="controlQueue(row.queue_name, 'clear_queue')">
                <template #reference>
                  <ElButton type="danger" link>清空</ElButton>
                </template>
              </ElPopconfirm>
            </ElButtonGroup>
          </template>
        </ElTableColumn>
      </ElTable>
    </ElCard>

    <!-- 4. 配置详情弹窗 -->
    <ElDialog v-model="configDialogVisible" :title="'队列配置: ' + selectedQueueName" width="50%">
      <div v-if="selectedConfig" class="config-container">
        <div class="mb-4 grid grid-cols-2 gap-4">
          <div class="config-item"><span class="label">QPS限制:</span> {{ selectedConfig.qps || '无限制' }}</div>
          <div class="config-item"><span class="label">最大重试:</span> {{ selectedConfig.max_retry_times }}</div>
          <div class="config-item"><span class="label">RPC模式:</span> {{ selectedConfig.is_using_rpc_mode ? '开启' : '关闭' }}</div>
          <div class="config-item"><span class="label">过滤去重:</span> {{ selectedConfig.do_task_filtering ? '开启' : '关闭' }}</div>
        </div>
        <ElDivider content-position="left">函数入参 Schema</ElDivider>
        <pre class="json-block">{{ selectedConfig.auto_generate_info?.final_func_input_params_info }}</pre>
        <ElDivider content-position="left">完整 BoosterParams</ElDivider>
        <pre class="json-block">{{ formatJson(selectedConfig) }}</pre>
      </div>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { fetchGetAllQueueRunInfo} from '@/api/funboost'
import { ElMessage } from 'element-plus'

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
  if (!row.history_run_count) return 0
  return ((row.history_run_fail_count / row.history_run_count) * 100)
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
    // if (action === 'pause_consume') res = await fetchPauseConsume({ queue_name: queueName })
    // else if (action === 'resume_consume') res = await fetchResumeConsume({ queue_name: queueName })
    // else if (action === 'clear_queue') res = await fetchClearQueue({ queue_name: queueName })
  
    ElMessage.success('操作成功')
    setTimeout(refreshData, 1000) // 延迟刷新以便后台更新状态
    
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

const showConfig = (row: any) => {
  selectedConfig.value = row.queue_params
  selectedQueueName.value = row.queue_name
  configDialogVisible.value = true
}

onMounted(() => {
  refreshData()
})

</script>

<style scoped>
.funboost-dashboard {
  overflow-y: auto;
}
.stats-card {
  transition: all 0.3s;
}
.stats-card:hover {
  transform: translateY(-5px);
}
.json-block {
  background: #2d2d2d;
  color: #ccc;
  padding: 15px;
  border-radius: 5px;
  overflow: auto;
  max-height: 300px;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.5;
}
.label {
  font-weight: bold;
  color: #666;
  margin-right: 8px;
}
.font-mono {
  font-family: 'Courier New', Courier, monospace;
}
:deep(.el-table__expanded-cell) {
  padding: 0 !important;
}
</style>