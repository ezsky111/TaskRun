<template>
  <div class="querytask-page art-full-height">
    <!-- 搜索栏 -->
    <QueryTaskSearch v-model="searchForm" @search="handleSearch" @reset="resetSearchParams" />

    <ElCard class="art-table-card" shadow="never">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-lg font-medium">任务查询</span>
          <ElButton type="primary" @click="showPublishDialog">
            <ElIcon><Plus /></ElIcon>
            创建任务
          </ElButton>
        </div>
      </template>

      <!-- 表格头部 -->
      <ArtTableHeader v-if="!isMobile" v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
      </ArtTableHeader>

      <!-- PC端表格 -->
      <ArtTable v-if="!isMobile" :loading="loading" :data="data" :columns="columns" :pagination="pagination"
        @pagination:size-change="handleSizeChange" @pagination:current-change="handleCurrentChange">
      </ArtTable>

      <!-- 移动端卡片列表 -->
      <div v-else class="grid grid-cols-1">
        <ElCard v-for="(item, index) in data" :key="item._id || index"  class="art-table-card">
          <div class="flex justify-between items-start mb-2">
            <div class="font-semibold text-lg">{{ item.function }}</div>
            <ElTag :type="getSuccessStatusConfig(item.success).type" size="small">
              {{ getSuccessStatusConfig(item.success).text }}
            </ElTag>
          </div>
          <div class="text-sm text-gray-600 mb-1"><strong>队列名称:</strong> {{ item.queue_name }}</div>
          <div class="text-sm text-gray-600 mb-1"><strong>主机名:</strong> {{ item.host_name }}</div>
          <div class="text-sm text-gray-600 mb-1"><strong>耗时:</strong> {{ item.time_cost?.toFixed(2) }}s</div>
          <div class="text-sm text-gray-600 mb-1"><strong>运行次数:</strong> {{ item.run_times }}</div>
          <div class="text-sm text-gray-600 mb-1"><strong>插入时间:</strong> {{ formatDateTime(item.insert_time) }}</div>
          <div class="text-sm text-gray-600 mb-2"><strong>参数:</strong> <span class="truncate block">{{ item.params_str }}</span></div>
          <ElButton size="small" @click="showDetail(item)">详情</ElButton>
        </ElCard>
      </div>

      <!-- 分页 -->
      <div v-if="isMobile" class="flex justify-center mt-4">
        <ElPagination
          :current-page="pagination.current"
          :page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </ElCard>

    <!-- 详情弹窗 -->
    <ElDialog v-model="detailDialogVisible" title="任务详情" :width="isMobile ? '90%' : '50%'" class="rounded-lg shadow-lg">
      <div v-if="detailData" class="p-4">
        <div class="flex flex-col lg:flex-row justify-between gap-4">
          <div class="w-full lg:w-1/2 bg-gray-100 p-4 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">参数</h3>
            <pre class="text-sm overflow-auto" v-html="highlightJson(formatJson(detailData.params))"></pre>
          </div>
          <div v-if="detailData.success" class="w-full lg:w-1/2 bg-gray-100 p-4 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">结果</h3>
            <pre class="text-sm overflow-auto" v-html="highlightJson(formatJson(detailData.result))"></pre>
          </div>
          <div v-else class="w-full lg:w-1/2 bg-gray-100 p-4 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">异常信息</h3>
            <pre class="text-sm">异常类型: {{ detailData.exception_type }}</pre>
            <pre class="text-sm">异常信息: {{ detailData.exception_msg }}</pre>
            <pre class="text-sm">完整信息: {{ detailData.exception }}</pre>
          </div>
        </div>
      </div>
    </ElDialog>

    <!-- 发布任务弹窗 -->
    <PublishTaskDialog
      v-model="publishDialogVisible"
      @published="handleTaskPublished"
      @view-result="handleViewResult"
    />
  </div>
</template>

<script setup lang="ts">
import { useTable } from '@/hooks/core/useTable'
import { fetchGetFunboostResults } from '@/api/funboost'
import QueryTaskSearch from './modules/querytask-search.vue'
import PublishTaskDialog from './modules/create-task.vue'
import { ElTag, ElDialog, ElButton, ElPagination, ElIcon } from 'element-plus'
import { ref, h, watch, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const route = useRoute()

defineOptions({ name: 'QueryTask' })

// 屏幕宽度检测
const screenWidth = ref(0)
const isMobile = computed(() => screenWidth.value < 768)

onMounted(() => {
  screenWidth.value = window.innerWidth
  const updateWidth = () => screenWidth.value = window.innerWidth
  window.addEventListener('resize', updateWidth)
  onUnmounted(() => window.removeEventListener('resize', updateWidth))
})

// 监听路由查询参数变化，自动执行查询
watch(() => route.query, (newQuery) => {
  if (newQuery.queue_name) {
    searchForm.value.queue_name = newQuery.queue_name as string
    handleSearch(searchForm.value)
  }
}, { immediate: true })

type FunboostResultItem = Api.Funboost.FunboostResultItem

// 搜索表单
const searchForm = ref({
  task_id: '',
  queue_name: '',
  success: undefined
})

// 发布任务弹窗
const publishDialogVisible = ref(false)

// 成功状态配置
const SUCCESS_STATUS_CONFIG = {
  true: { type: 'success' as const, text: '成功' },
  false: { type: 'danger' as const, text: '失败' }
} as const

/**
 * 获取成功状态配置
 */
const getSuccessStatusConfig = (success: boolean) => {
  return SUCCESS_STATUS_CONFIG[success as unknown as keyof typeof SUCCESS_STATUS_CONFIG] || { type: 'info' as const, text: '未知' }
}

const {
  columns,
  columnChecks,
  data,
  loading,
  pagination,
  getData,
  searchParams,
  resetSearchParams,
  handleSizeChange,
  handleCurrentChange,
  refreshData
} = useTable({
  // 核心配置
  core: {
    apiFn: fetchGetFunboostResults,
    apiParams: {
      page: 1,
      size: 20,
      ...searchForm.value
    },
    // 自定义分页字段映射
    paginationKey: {
      current: 'page',
      size: 'size'
    },
    columnsFactory: () => [
      { type: 'index', width: 60, label: '序号' },
      { prop: 'function', label: '函数名' },
      { prop: 'queue_name', label: '队列名称' },
      { prop: 'host_name', label: '主机名' },
      { prop: 'params_str', label: '参数' },
      { prop: 'time_cost', label: '耗时(s)', formatter: (row: FunboostResultItem) => row.time_cost?.toFixed(2) },
      { prop: 'run_times', label: '运行次数', width: 80 },
      {
        prop: 'success', label: '状态', width: 80, formatter: (row: FunboostResultItem) => {
          const statusConfig = getSuccessStatusConfig(row.success)
          return h(ElTag, { type: statusConfig.type }, () => statusConfig.text)
        }
      },
      { prop: 'insert_time', label: '插入时间', width: 180, formatter: (row: FunboostResultItem) => formatDateTime(row.insert_time) },
      {
        label: '操作', width: 120, fixed: 'right', formatter: (row: FunboostResultItem) => {
          return h(ElButton, {
            onClick: () => showDetail(row)
          }, '详情')
        }
      }
    ]
  },
  // 数据处理
  transform: {
    dataTransformer: (data: Api.Funboost.FunboostResultItem[]) => {
      return data || []
    }
  }
})

// 详情弹窗相关
const detailDialogVisible = ref(false)
const detailData = ref<FunboostResultItem | null>(null)

const showDetail = (row: FunboostResultItem) => {
  detailData.value = row
  detailDialogVisible.value = true
}

// 发布任务相关方法
const showPublishDialog = () => {
  publishDialogVisible.value = true
}

const handleTaskPublished = () => {
  // 任务发布成功后刷新列表
  refreshData()
}

const handleViewResult = (taskId: string) => {
  // 设置任务ID到搜索表单并查询
  searchForm.value.task_id = taskId
  handleSearch(searchForm.value)
}

/**
 * 格式化 JSON 数据
 */
const formatJson = (data: any) => {
  try {
    const decompressed = JSON.parse(data) // 假设 data 是压缩后的 JSON 字符串
    return JSON.stringify(decompressed, null, 2)
  } catch {
    return data
  }
}

/**
 * 高亮 JSON 数据
 */
const highlightJson = (json: string) => {
  return hljs.highlight(json, { language: 'json' }).value
}

/**
 * 搜索处理
 */
const handleSearch = (params: Record<string, any>) => {
  Object.assign(searchParams, params)
  getData()
}

/**
 * 格式化日期时间
 */
const formatDateTime = (dateTime: string) => {
  try {
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    };
    return new Date(dateTime).toLocaleString('zh-CN', options);
  } catch {
    return dateTime;
  }
};
</script>

<style scoped>
.querytask-page {
  padding: 20px;
}

.art-table-card {
  margin-top: 20px;
}

.el-dialog__body {
  padding: 20px;
}
</style>