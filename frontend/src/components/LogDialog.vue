<template>
  <el-dialog v-model="visible" title="进程日志" width="800px" @close="handleClose">
    <div class="log-header">
      <div class="status-info">
        <span>进程状态: </span>
        <el-tag :type="processStatus.status === 'running' ? 'success' : 'danger'">
          {{ processStatus.status === 'running' ? '运行中' : '已停止' }}
        </el-tag>
        <span v-if="processStatus.pid">PID: {{ processStatus.pid }}</span>
      </div>
    </div>
    <div class="log-container" ref="logContainerRef">
      <pre class="log-content">{{ logs.join('\n') }}</pre>
    </div>
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshLogs">刷新</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { fetchLogs, fetchGetProcessStatus } from '@/api/system-manage'
import type { Api } from '@/types/api'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const logs = ref<string[]>([])
const logContainerRef = ref<HTMLElement>()
const processStatus = ref<Api.SystemManage.ProcessStatusData>({ status: 'stopped' })
let logInterval: number | null = null

// 监听外部visible变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    startRefreshing()
  } else {
    stopRefreshing()
  }
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 刷新日志和进程状态
const refreshLogs = async () => {
  try {
    const [logRes, statusRes] = await Promise.all([
      fetchLogs(),
      fetchGetProcessStatus()
    ])
    // 只显示最新的100行以优化性能
    logs.value = logRes.logs.slice(-100)
    processStatus.value = statusRes
    // 自动滚动到底部
    await nextTick()
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
    }
  } catch (err) {
    console.error('获取日志或状态失败', err)
  }
}

// 开始刷新
const startRefreshing = () => {
  refreshLogs()
  logInterval = setInterval(refreshLogs, 5000)
}

// 停止刷新
const stopRefreshing = () => {
  if (logInterval) {
    clearInterval(logInterval)
    logInterval = null
  }
}

// 关闭处理
const handleClose = () => {
  stopRefreshing()
  visible.value = false
}

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
  gap: 10px;
}

.status-info {
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
}

.log-content {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 10px;
  margin: 0;
  color: #333;
}
</style>