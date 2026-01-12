<template>
  <ElDialog
    v-model="visible"
    title="发布任务"
    :width="isMobile ? '95%' : '800px'"
    :close-on-click-modal="false"
    class="publish-task-dialog"
  >
    <div class="publish-task-content">
      <!-- 队列选择 -->
      <div class="mb-6">
        <ElFormItem label="选择队列" required>
          <ElSelect
            v-model="selectedQueue"
            placeholder="请选择队列"
            class="w-full"
            @change="handleQueueChange"
            :loading="loadingQueues"
          >
            <ElOption
              v-for="queueName in queueNames"
              :key="queueName"
              :label="queueName"
              :value="queueName"
            />
          </ElSelect>
        </ElFormItem>
      </div>

      <!-- 入参JSON -->
      <div v-if="selectedQueue" class="mb-6">
        <h3 class="text-lg font-medium mb-4">任务参数 (JSON格式)</h3>
        <ElForm :model="jsonForm" :rules="jsonRules" ref="jsonFormRef">
          <ElFormItem prop="jsonData" :required="inputParams.some((p: { required: any; }) => p.required)">
            <ElInput
              v-model="jsonForm.jsonData"
              type="textarea"
              :rows="8"
              placeholder='请输入JSON格式的参数，例如：{"param1": "value1", "param2": 123}'
              class="font-mono"
            />
            <div class="text-sm text-gray-500 mt-2">
              <p>支持的参数：</p>
              <ul class="list-disc list-inside">
                <li v-for="param in inputParams" :key="param.name">
                  <span :class="param.required ? 'text-red-500' : 'text-gray-600'">
                    {{ param.name }}
                    <span v-if="param.required" class="text-red-500">*</span>
                  </span>
                </li>
              </ul>
              <p class="text-red-500">* 为必填参数</p>
            </div>
          </ElFormItem>
        </ElForm>
      </div>

      <!-- 发布选项 -->
      <div v-if="selectedQueue" class="mb-6">
        <h3 class="text-lg font-medium mb-4">发布选项</h3>
        <ElRow :gutter="20">
          <ElCol :xs="24" :sm="12">
            <ElFormItem label="需要结果">
              <ElSwitch v-model="needResult" />
            </ElFormItem>
          </ElCol>
          <ElCol :xs="24" :sm="12">
            <ElFormItem label="超时时间(秒)">
              <ElInputNumber
                v-model="timeout"
                :min="1"
                :max="3600"
                placeholder="默认60秒"
              />
            </ElFormItem>
          </ElCol>
        </ElRow>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end space-x-4">
        <ElButton @click="handleCancel">取消</ElButton>
        <ElButton
          type="primary"
          :loading="publishing"
          @click="handlePublish"
          :disabled="!selectedQueue"
        >
          发布任务
        </ElButton>
      </div>
    </template>

    <!-- 发布结果弹窗 -->
    <ElDialog
      v-model="resultDialogVisible"
      title="发布结果"
      :width="isMobile ? '90%' : '600px'"
      append-to-body
    >
      <div v-if="publishResult">
        <!-- 推送成功提示 -->
        <div class="mb-4">
          <ElAlert
            type="success"
            title="任务推送成功"
            :description="needResult ? '任务已执行完毕' : '任务已成功推送至队列'"
            show-icon
            class="mb-4"
          />
        </div>

        <!-- 任务基本信息 -->
        <div class="mb-4">
          <h4 class="text-md font-medium mb-2">任务信息</h4>
          <div class="bg-gray-50 p-3 rounded text-sm">
            <p><strong>任务ID:</strong> {{ publishResult.task_id || '无' }}</p>
            <p><strong>队列名称:</strong> {{ selectedQueue }}</p>
            <p><strong>是否需要结果:</strong> {{ needResult ? '是' : '否' }}</p>
          </div>
        </div>

        <!-- 函数执行结果 -->
        <div v-if="needResult && publishResult.status_and_result" class="mb-4">
          <h4 class="text-md font-medium mb-2">执行结果</h4>
          <div class="border rounded p-3">
            <div class="mb-3">
              <ElAlert
                :type="publishResult.status_and_result.success ? 'success' : 'error'"
                :title="publishResult.status_and_result.success ? '执行成功' : '执行失败'"
                show-icon
                class="mb-3"
              />
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm mb-3">
              <div>
                <p><strong>函数名:</strong> {{ publishResult.status_and_result.function }}</p>
                <p><strong>执行耗时:</strong> {{ publishResult.status_and_result.time_cost?.toFixed(2) }}s</p>
                <p><strong>运行次数:</strong> {{ publishResult.status_and_result.run_times }}</p>
              </div>
              <div>
                <p><strong>开始时间:</strong> {{ publishResult.status_and_result.time_start ? new Date(publishResult.status_and_result.time_start * 1000).toLocaleString() : '未知' }}</p>
                <p><strong>结束时间:</strong> {{ publishResult.status_and_result.time_end ? new Date(publishResult.status_and_result.time_end * 1000).toLocaleString() : '未知' }}</p>
                <p><strong>运行状态:</strong> {{ publishResult.status_and_result.run_status }}</p>
              </div>
            </div>

            <!-- 执行成功时显示结果 -->
            <div v-if="publishResult.status_and_result.success" class="mb-3">
              <p class="font-medium text-green-600">执行结果:</p>
              <div class="bg-green-50 p-2 rounded border text-sm font-mono">
                {{ JSON.stringify(publishResult.status_and_result.result, null, 2) }}
              </div>
            </div>

            <!-- 执行失败时显示异常 -->
            <div v-else class="mb-3">
              <p class="font-medium text-red-600">异常信息:</p>
              <div class="bg-red-50 p-2 rounded border text-sm">
                <p><strong>异常类型:</strong> {{ publishResult.status_and_result.exception_type }}</p>
                <p><strong>异常消息:</strong> {{ publishResult.status_and_result.exception_msg }}</p>
                <details class="mt-2">
                  <summary class="cursor-pointer text-blue-600">完整异常堆栈</summary>
                  <pre class="bg-red-100 p-2 rounded text-xs mt-1 whitespace-pre-wrap">{{ publishResult.status_and_result.exception }}</pre>
                </details>
              </div>
            </div>

            <!-- 参数信息 -->
            <div class="mb-3">
              <p class="font-medium">输入参数:</p>
              <div class="bg-blue-50 p-2 rounded border text-sm font-mono">
                {{ publishResult.status_and_result.params_str }}
              </div>
            </div>
          </div>
        </div>

        <!-- 如果需要结果但还没有执行完成 -->
        <div v-if="needResult && !publishResult.status_and_result" class="text-center text-gray-500">
          <p>任务正在执行中，请稍后查看结果...</p>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-between">
          <ElButton @click="resultDialogVisible = false">关闭</ElButton>
          <div class="flex space-x-2">
            <ElButton
              v-if="publishResult && publishResult.task_id"
              @click="handleViewLogs"
            >
              查看相关日志
            </ElButton>
            <ElButton
              v-if="publishResult && publishResult.task_id"
              type="primary"
              @click="handleViewResult"
            >
              查看结果
            </ElButton>
          </div>
        </div>
      </template>
    </ElDialog>
  </ElDialog>

  <!-- 日志对话框 -->
  <LogDialog ref="logDialogRef" v-model="logDialogVisible" log-type="process" />
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchGetQueuesConfig, fetchPublishMsg } from '@/api/funboost'
import LogDialog from '@/components/LogDialog.vue'

// Props
interface Props {
  modelValue: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'published': []
  'view-result': [taskId: string]
}>()

// 响应式数据
const loadingQueues = ref(false)
const publishing = ref(false)
const selectedQueue = ref('')
const queueConfigs = ref<Record<string, any>>({})
const jsonForm = reactive({ jsonData: '{}' })
const jsonRules = ref({
  jsonData: [
    { required: true, message: '请输入JSON格式的参数', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!value) return callback()
        try {
          JSON.parse(value)
          callback()
        } catch (error) {
          callback(new Error('JSON格式不正确'))
        }
      },
      trigger: 'blur'
    }
  ]
})
const needResult = ref(false)
const timeout = ref(60)
const resultDialogVisible = ref(false)
const publishResult = ref<any>(null)
const jsonFormRef = ref()
const logDialogRef = ref()
const logDialogVisible = ref(false)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 计算属性
const queueNames = computed(() => Object.keys(queueConfigs.value))

const inputParams = computed(() => {
  if (!selectedQueue.value || !queueConfigs.value[selectedQueue.value]) {
    return []
  }

  const queueConfig = queueConfigs.value[selectedQueue.value]
  const autoGenerateInfo = queueConfig.auto_generate_info

  if (!autoGenerateInfo) {
    return []
  }

  const allArgNameList = autoGenerateInfo.final_func_input_params_info.all_arg_name_list || []
  const mustArgNameList = autoGenerateInfo.final_func_input_params_info.must_arg_name_list || []
  const paramsInfo = autoGenerateInfo.final_func_input_params_info || {}

  return allArgNameList.map((name: string) => {
    const info = paramsInfo[name] || {}
    return {
      name,
      type: info.annotation || 'string',
      default: info.default,
      required: mustArgNameList.includes(name)
    }
  })
})

const isMobile = computed(() => {
  return window.innerWidth < 768
})

// 方法
const loadQueuesConfig = async () => {
  try {
    loadingQueues.value = true
    const response = await fetchGetQueuesConfig()
    queueConfigs.value = response.queues_config
  } catch (error) {
    ElMessage.error('获取队列配置失败')
    console.error(error)
  } finally {
    loadingQueues.value = false
  }
}

const handleQueueChange = () => {
  // 根据选择的队列设置默认JSON
  if (selectedQueue.value && queueConfigs.value[selectedQueue.value]) {
    const params = inputParams.value
    const defaultObj: Record<string, any> = {}

    params.forEach((param: { default: undefined; name: string | number; type: any; }) => {
      if (param.default !== undefined) {
        defaultObj[param.name] = param.default
      } else {
        // 设置默认值
        switch (param.type) {
          case 'string':
            defaultObj[param.name] = ''
            break
          case 'number':
            defaultObj[param.name] = 0
            break
          case 'boolean':
            defaultObj[param.name] = false
            break
          default:
            defaultObj[param.name] = null
        }
      }
    })

    jsonForm.jsonData = JSON.stringify(defaultObj, null, 2)
  } else {
    jsonForm.jsonData = '{}'
  }
}

const handlePublish = async () => {
  if (!selectedQueue.value) {
    ElMessage.warning('请选择队列')
    return
  }

  try {
    await jsonFormRef.value.validate()
  } catch (error) {
    return
  }

  let msgBody: any
  try {
    msgBody = JSON.parse(jsonForm.jsonData)
  } catch (error) {
    ElMessage.error('JSON格式不正确')
    return
  }

  // 验证必填参数
  const requiredParams = inputParams.value.filter((p: { required: any; }) => p.required)
  const missingParams = requiredParams.filter((p: { name: string; }) => !(p.name in msgBody) || msgBody[p.name] === null || msgBody[p.name] === undefined || msgBody[p.name] === '')

  if (missingParams.length > 0) {
    ElMessage.error(`缺少必填参数: ${missingParams.map((p: { name: any; }) => p.name).join(', ')}`)
    return
  }

  try {
    publishing.value = true
    const params = {
      queue_name: selectedQueue.value,
      msg_body: msgBody,
      need_result: needResult.value,
      timeout: timeout.value
    }

    const response = await fetchPublishMsg(params)
    publishResult.value = response
    resultDialogVisible.value = true

    ElMessage.success('任务发布成功')
    emit('published')
  } catch (error) {
    ElMessage.error('任务发布失败')
    console.error(error)
  } finally {
    publishing.value = false
  }
}

const handleCancel = () => {
  visible.value = false
  resetForm()
}

const handleViewResult = () => {
  if (publishResult.value && publishResult.value.task_id) {
    emit('view-result', publishResult.value.task_id)
    resultDialogVisible.value = false
    visible.value = false
  }
}

const handleViewLogs = () => {
  if (publishResult.value && publishResult.value.task_id && logDialogRef.value) {
    // 设置过滤关键词并打开日志对话框
    logDialogRef.value.setFilterKeyword(publishResult.value.task_id)
    logDialogRef.value.open()
    // 自动关闭发布结果对话框，只显示日志
    resultDialogVisible.value = false
  }
}

const resetForm = () => {
  selectedQueue.value = ''
  jsonForm.jsonData = '{}'
  needResult.value = false
  timeout.value = 60
  jsonFormRef.value?.clearValidate()
}

// 生命周期
onMounted(() => {
  if (visible.value) {
    loadQueuesConfig()
  }
})

// 监听visible变化，打开时加载数据
watch(visible, (newVal) => {
  if (newVal && Object.keys(queueConfigs.value).length === 0) {
    loadQueuesConfig()
  }
})
</script>

<style scoped>
.publishtask-page {
  background-color: #f5f5f5;
}

.art-table-card {
  margin-bottom: 20px;
}

/* 移动端样式调整 */
@media (max-width: 767px) {
  .publishtask-page {
    padding: 1rem;
  }

  .el-form-item__label {
    font-size: 14px;
  }

  .el-input,
  .el-select,
  .el-input-number {
    font-size: 14px;
  }
}
</style>
