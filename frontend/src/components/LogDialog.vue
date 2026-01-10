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
    </div>
    <div class="log-container" ref="logContainerRef">
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

// 创建 ansi_up 实例
const ansiUp = new AnsiUp()

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
  // 限制显示最新的1000行以优化性能
  const recentLogs = logs.value.slice(-1000)
  
  // 将每行日志通过 ansi_up 转换为HTML
  const htmlLogs = recentLogs.map(log => {
    return ansiUp.ansi_to_html(log)
  })
  
  // 每行用div包裹，并添加行号
  return htmlLogs.map((html, index) => {
    const lineNumber = index + 1 + Math.max(0, logs.value.length - 1000)
    return `<div class="log-line"><span class="line-number">${lineNumber}:</span>${html}</div>`
  }).join('')
})

// 监听外部visible变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    connectSSE()
    if (props.logType === 'process') {
      updateProcessStatus()
    }
  } else {
    disconnectSSE()
    logs.value = []
  }
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 监听日志变化，自动滚动
watch(() => logs.value.length, () => {
  if (autoScroll.value) {
    scrollToBottom()
  }
})

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
    }
    
    eventSource.value.onmessage = (event) => {
      const logLine = event.data
      logs.value.push(logLine)
      
      // 限制内存中的日志行数
      if (logs.value.length > 2000) {
        logs.value = logs.value.slice(-1000)
      }
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

// 断开SSE连接
const disconnectSSE = () => {
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
}

// 关闭处理
const handleClose = () => {
  disconnectSSE()
  visible.value = false
}

// 组件卸载时清理
onUnmounted(() => {
  disconnectSSE()
})

// 暴露方法给父组件
defineExpose({
  open: () => {
    visible.value = true
  },
  close: () => {
    handleClose()
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