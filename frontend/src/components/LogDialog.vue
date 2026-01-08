<template>
  <el-dialog v-model="visible" :title="logType === 'process' ? '进程日志' : '安装日志'" width="80%" @close="handleClose">
    <div class="log-header" v-if="logType === 'process'">
      <div class="status-info">
        <span>进程状态: </span>
        <el-tag :type="processStatus.status === 'running' ? 'success' : 'danger'">
          {{ processStatus.status === 'running' ? '运行中' : '已停止' }}
        </el-tag>
        <span v-if="processStatus.pid">PID: {{ processStatus.pid }}</span>
      </div>
    </div>
    <div class="log-container" ref="logContainerRef">
      <!-- 使用 v-html 渲染解析后的HTML -->
      <div class="log-content" v-html="formattedLogs"></div>
    </div>
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="refreshLogs">刷新</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { fetchLogs, fetchGetProcessStatus, fetchInstallLogs } from '@/api/system-manage'
import type { Api } from '@/types/api'
import {  AnsiUp } from 'ansi_up' // 导入 ansi_up

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
let logInterval: number | null = null

// 创建 ansi_up 实例
const ansiUp = new AnsiUp()

// 计算属性：将日志数组转换为带颜色的HTML
const formattedLogs = computed(() => {
  // 只处理最新的100行以优化性能
  const recentLogs = logs.value.slice(-100)
  
  // 将每行日志通过 ansi_up 转换为HTML
  const htmlLogs = recentLogs.map(log => {
    // 使用 ansi_to_html 方法解析ANSI颜色代码
    return ansiUp.ansi_to_html(log)
  })
  
  // 每行用div包裹，并添加行号
  return htmlLogs.map((html, index) => {
    const lineNumber = index + 1 + Math.max(0, logs.value.length - 100)
    return `<div class="log-line"><span class="line-number">${lineNumber}:</span>${html}</div>`
  }).join('')
})

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
    if (props.logType === 'process') {
      const [logRes, statusRes] = await Promise.all([
        fetchLogs(),
        fetchGetProcessStatus()
      ])
      // 保持原始日志数据
      logs.value = logRes.logs.slice(-100)
      processStatus.value = statusRes
    } else {
      const logRes = await fetchInstallLogs()
      logs.value = logRes.logs.slice(-100)
    }
    // 自动滚动到底部
    await nextTick()
  } catch (err) {
    console.error('获取日志或状态失败', err)
  }
}

// 滚动到底部函数
const scrollToBottom = () => {
  if (logContainerRef.value) {
    // 使用 requestAnimationFrame 确保在DOM更新后执行
    requestAnimationFrame(() => {
      if (logContainerRef.value) {
        logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
      }
    })
  }
}

// 开始刷新
const startRefreshing = () => {
  refreshLogs()
  // 保持原有的5秒刷新间隔
  logInterval = window.setInterval(refreshLogs, 5000)
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

// 组件卸载时清理定时器
onUnmounted(() => {
  stopRefreshing()
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