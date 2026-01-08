<template>
  <ElCard class="art-table-card mb-5" shadow="never">
    <template #header>
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold">子进程管理</h3>
        <ElButton :icon="Refresh" @click="refreshProcessStatus" :loading="processLoading.status" size="small">刷新状态</ElButton>
      </div>
    </template>

    <div class="grid grid-cols-1 p-5 md:grid-cols-3 gap-4">
      <div class="stat-item">
        <div class="stat-title">进程状态</div>
        <div class="stat-value" :style="{ color: processStatus.status === 'running' ? '#67C23A' : '#F56C6C' }">
          {{ processStatus.status === 'running' ? '运行中' : '已停止' }}
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-title">进程ID</div>
        <div class="stat-value">{{ processStatus.pid }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-title">消费进程</div>
        <div class="stat-value" style="color: #409EFF;">taskrunner.py</div>
      </div>
    </div>

    <ElSpace wrap class="p-5">
      <ElButton
        type="primary"
        :loading="processLoading.start"
        :disabled="processStatus.status === 'running'"
        @click="handleStartProcess"
      >
        启动进程
      </ElButton>
      <ElButton
        type="warning"
        :loading="processLoading.restart"
        @click="handleRestartProcess"
      >
        重启进程
      </ElButton>
      <ElButton
        type="danger"
        :loading="processLoading.stop"
        :disabled="processStatus.status === 'stopped'"
        @click="handleStopProcess"
      >
        停止进程
      </ElButton>
      <ElButton
        type="info"
        @click="logDialogVisible = true"
      >
        查看日志
      </ElButton>
    </ElSpace>

    <!-- 日志弹窗 -->
    <LogDialog v-model="logDialogVisible" />
  </ElCard>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { fetchStartProcess, fetchRestartProcess, fetchStopProcess, fetchGetProcessStatus } from '@/api/system-manage'
import { ElMessage, ElCard, ElButton, ElSpace } from 'element-plus'
import LogDialog from '@/components/LogDialog.vue'

// 进程管理数据
const processStatus = ref<Api.SystemManage.ProcessStatusData>({
  status: 'stopped'
})
const processLoading = ref({
  start: false,
  restart: false,
  stop: false,
  status: false
})

// 日志弹窗
const logDialogVisible = ref(false)

// 刷新进程状态
const refreshProcessStatus = async () => {
  processLoading.value.status = true
  try {
    const res = await fetchGetProcessStatus()
    processStatus.value = res
  } catch (err) {
    ElMessage.error('获取进程状态失败')
  } finally {
    processLoading.value.status = false
  }
}

// 启动进程
const handleStartProcess = async () => {
  processLoading.value.start = true
  try {
    await fetchStartProcess()
    ElMessage.success('进程启动中')
    logDialogVisible.value = true
    await refreshProcessStatus()
  } catch (err) {
    ElMessage.error('启动失败')
  } finally {
    processLoading.value.start = false
  }
}

// 重启进程
const handleRestartProcess = async () => {
  processLoading.value.restart = true
  try {
    await fetchRestartProcess()
    ElMessage.success('进程重启中')
    logDialogVisible.value = true
    await refreshProcessStatus()
  } catch (err) {
    ElMessage.error('重启失败')
  } finally {
    processLoading.value.restart = false
  }
}

// 停止进程
const handleStopProcess = async () => {
  processLoading.value.stop = true
  try {
    await fetchStopProcess()
    ElMessage.success('进程停止成功')
    await refreshProcessStatus()
  } catch (err) {
    ElMessage.error('停止失败')
  } finally {
    processLoading.value.stop = false
  }
}

onMounted(() => {
  refreshProcessStatus()
})
</script>

<style>
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