<template>
  <el-dialog v-model="visible" :title="logType === 'process' ? '进程日志' : '安装日志'" width="80%" @close="handleClose">
    <div class="log-header">
      <div class="status-info" v-if="logType === 'process'">
        <span>进程状态: </span>
        <el-tag :type="processStatus.status === 'running' ? 'success' : 'danger'">
          {{ processStatus.status === 'running' ? '运行中' : '已停止' }}
        </el-tag>
        <span v-if="processStatus.pid">PID: {{ processStatus.pid }}</span>
      </div>
      <div class="connection-status">
        <span>连接状态: </span>
        <el-tag :type="connectionStatusType">
          {{ connectionStatusText }}
        </el-tag>
      </div>
      <div class="filter-section">
        <el-input
          v-model="filterKeyword"
          placeholder="筛选日志（支持正则表达式）"
          clearable
          style="width: 300px"
        />
        <span class="filter-count">{{ filteredLogs.length }} / {{ logs.length }}</span>
      </div>
    </div>
    <div class="log-container" ref="logContainerRef" @scroll="handleScroll">
      <!-- 使用 v-html 渲染解析后的HTML -->
      <div class="log-content" v-html="formattedLogs"></div>
    </div>
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="clearLogs">清空日志</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onUnmounted } from 'vue'
import { fetchGetProcessStatus } from '@/api/system-manage'
import { AnsiUp } from 'ansi_up'
import { useUserStore } from '@/store/modules/user'
import { debounce } from '@/utils/index'

interface Props {
  modelValue: boolean
  logType?: 'process' | 'install'
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  logType: 'process'
})
const emit = defineEmits<Emits>()

const visible = ref(false)
const logs = ref<string[]>([])
const logContainerRef = ref<HTMLElement>()
const processStatus = ref<Api.SystemManage.ProcessStatusData>({ status: 'stopped' })
const eventSource = ref<EventSource | null>(null)
const connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')
const autoScroll = ref(true)
const filterKeyword = ref('')
const pendingLogs = ref<string[]>([]) // 待处理的日志缓冲区
const isProcessingLogs = ref(false) // 是否正在处理日志

// 创建 ansi_up 实例
const ansiUp = new AnsiUp()

// 每次处理的日志行数（增大以加快显示）
const BATCH_SIZE = 200
// 最多保留的日志行数
const MAX_LOG_LINES = 5000
// 处理日志的时间间隔（毫秒）（减少以更频繁处理）
const PROCESS_INTERVAL = 50
// 用于缓存formattedLogs的最后一次过滤结果
const cachedFilteredLogsLength = ref(0)
const shouldUpdateContent = ref(true)

// 过滤日志（防抖处理）
const filteredLogs = computed(() => {
  if (!filterKeyword.value) {
    return logs.value
  }
  
  try {
    // 尝试作为正则表达式处理
    const regex = new RegExp(filterKeyword.value, 'i')
    return logs.value.filter(log => regex.test(log))
  } catch {
    // 如果正则表达式无效，则作为普通字符串进行模糊匹配
    return logs.value.filter(log => log.toLowerCase().includes(filterKeyword.value.toLowerCase()))
  }
})

// 连接状态显示
const connectionStatusType = computed(() => {
  switch (connectionStatus.value) {
    case 'connected':
      return 'success'
    case 'connecting':
      return 'warning'
    case 'disconnected':
      return 'danger'
  }
})

const connectionStatusText = computed(() => {
  switch (connectionStatus.value) {
    case 'connected':
      return '已连接'
    case 'connecting':
      return '连接中...'
    case 'disconnected':
      return '已断开'
  }
})

// 计算属性：将日志数组转换为带颜色的HTML
const formattedLogs = computed(() => {
  if (!shouldUpdateContent.value && cachedFilteredLogsLength.value === filteredLogs.value.length) {
    return ''
  }
  
  cachedFilteredLogsLength.value = filteredLogs.value.length
  shouldUpdateContent.value = false
  
  // 限制显示最新的1000行以优化性能
  const recentLogs = filteredLogs.value.slice(-1000)
  
  // 将每行日志通过 ansi_up 转换为HTML
  const htmlLogs = recentLogs.map(log => {
    return ansiUp.ansi_to_html(log)
  })
  
  // 每行用div包裹，并添加行号
  return htmlLogs.map((html, index) => {
    const lineNumber = index + 1 + Math.max(0, filteredLogs.value.length - 1000)
    return `<div class="log-line"><span class="line-number">${lineNumber}:</span>${html}</div>`
  }).join('')
})

// 监听过滤关键词变化（设置标志以进行重新渲染）
watch(filterKeyword, () => {
  shouldUpdateContent.value = true
  debouncedScrollToBottom()
})

// 监听外部visible变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    autoScroll.value = true
    connectSSE()
    if (props.logType === 'process') {
      updateProcessStatus()
    }
  } else {
    disconnectSSE()
    logs.value = []
    pendingLogs.value = []
  }
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 监听日志变化，自动滚动（设置标志以进行重新渲染）
watch(() => logs.value.length, () => {
  shouldUpdateContent.value = true
  if (autoScroll.value) {
    scrollToBottom()
  }
})

// 防抖滚动（防止频繁滚动）
const debouncedScrollToBottom = debounce(() => {
  if (autoScroll.value) {
    scrollToBottom()
  }
}, 200)

// 连接SSE
const connectSSE = () => {
  // 先断开旧连接
  disconnectSSE()
  
  const url = props.logType === 'process' 
    ? '/api/logs/stream' 
    : '/api/install/logs/stream'
  
  connectionStatus.value = 'connecting'
  
  try {
    // 获取token
    const { accessToken } = useUserStore()
    const eventSourceUrl = accessToken ? `${url}?token=${accessToken}` : url
    
    eventSource.value = new EventSource(eventSourceUrl)
    
    eventSource.value.onopen = () => {
      connectionStatus.value = 'connected'
      console.log('SSE连接已建立')
      startProcessingLogs()
    }
    
    eventSource.value.onmessage = (event) => {
      const logLine = event.data
      // 将日志放入缓冲区而不是直接添加
      pendingLogs.value.push(logLine)
    }
    
    eventSource.value.onerror = (error) => {
      console.error('SSE连接错误:', error)
      connectionStatus.value = 'disconnected'
      disconnectSSE()
      
      // 如果对话框仍然打开，3秒后尝试重连
      if (visible.value) {
        setTimeout(() => {
          if (visible.value) {
            console.log('尝试重新连接SSE...')
            connectSSE()
          }
        }, 3000)
      }
    }
  } catch (error) {
    console.error('创建SSE连接失败:', error)
    connectionStatus.value = 'disconnected'
  }
}

// 启动日志处理定时器
let processLogsTimer: ReturnType<typeof setInterval> | null = null
const startProcessingLogs = () => {
  if (processLogsTimer) return
  
  processLogsTimer = setInterval(() => {
    if (pendingLogs.value.length > 0) {
      processNextBatch()
    }
  }, PROCESS_INTERVAL)
}

// 停止日志处理定时器
const stopProcessingLogs = () => {
  if (processLogsTimer) {
    clearInterval(processLogsTimer)
    processLogsTimer = null
  }
}

// 处理下一批日志
const processNextBatch = () => {
  if (isProcessingLogs.value || pendingLogs.value.length === 0) {
    return
  }
  
  isProcessingLogs.value = true
  
  requestAnimationFrame(() => {
    const batch = pendingLogs.value.splice(0, BATCH_SIZE)
    logs.value.push(...batch)
    
    // 限制内存中的日志行数，更激进的清理策略
    if (logs.value.length > MAX_LOG_LINES) {
      logs.value = logs.value.slice(-Math.ceil(MAX_LOG_LINES * 0.8))
    }
    
    isProcessingLogs.value = false
  })
}

// 断开SSE连接
const disconnectSSE = () => {
  stopProcessingLogs()
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
  connectionStatus.value = 'disconnected'
}

// 更新进程状态
const updateProcessStatus = async () => {
  try {
    const statusRes = await fetchGetProcessStatus()
    processStatus.value = statusRes
  } catch (err) {
    console.error('获取进程状态失败', err)
  }
}

// 滚动到底部函数
const scrollToBottom = () => {
  nextTick(() => {
    if (logContainerRef.value) {
      requestAnimationFrame(() => {
        if (logContainerRef.value) {
          logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
        }
      })
    }
  })
}

// 检测用户是否手动滚动
const handleScroll = () => {
  if (logContainerRef.value) {
    const { scrollTop, scrollHeight, clientHeight } = logContainerRef.value
    // 如果用户滚动到接近底部（50px内），启用自动滚动
    autoScroll.value = scrollHeight - scrollTop - clientHeight < 50
  }
}

// 清空日志
const clearLogs = () => {
  logs.value = []
  pendingLogs.value = []
}

// 关闭处理
const handleClose = () => {
  disconnectSSE()
  visible.value = false
  // 清理缓冲区
  pendingLogs.value = []
}

// 组件卸载时清理
onUnmounted(() => {
  disconnectSSE()
  stopProcessingLogs()
  pendingLogs.value = []
})

// 暴露方法给父组件
defineExpose({
  open: () => {
    visible.value = true
  },
  close: () => {
    handleClose()
  },
  setFilterKeyword: (keyword: string) => {
    filterKeyword.value = keyword
  }
})
</script>

<style scoped lang="scss">
.log-header {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.filter-count {
  font-size: 12px;
  color: #666;
  min-width: 80px;
  text-align: center;
}

.log-container {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #1e1e1e; /* 深色背景更适合显示彩色日志 */
}

/* 日志内容样式 */
.log-content {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  padding: 10px;
  margin: 0;
  color: #d4d4d4; /* 默认文字颜色 */
  white-space: pre-wrap; /* 保持换行 */
  word-wrap: break-word;
}

/* 为 ansi_up 生成的元素添加基础样式 */
.log-content :deep(span) {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
}

/* 行号样式 */
.log-content :deep(.log-line) {
  display: flex;
  min-height: 18px;
  border-bottom: 1px solid #2a2a2a;
  padding: 2px 0;
}

.log-content :deep(.line-number) {
  color: #6e7681;
  min-width: 60px;
  text-align: right;
  padding-right: 10px;
  user-select: none;
  border-right: 1px solid #2a2a2a;
  margin-right: 10px;
}
</style>