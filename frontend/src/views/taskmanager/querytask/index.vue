<template>
  <div class="querytask-page art-full-height">
    <!-- 搜索栏 -->
    <QueryTaskSearch v-model="searchForm" @search="handleSearch" @reset="resetSearchParams" />

    <ElCard class="art-table-card" shadow="never">
      <!-- 表格头部 -->
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
      </ArtTableHeader>

      <!-- 表格 -->
      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
      </ArtTable>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { useTable } from '@/hooks/core/useTable'
  import { fetchGetFunboostResults } from '@/api/funboost'
  import QueryTaskSearch from './modules/querytask-search.vue'
  import { ElTag } from 'element-plus'

  defineOptions({ name: 'QueryTask' })

  type FunboostResultItem = Api.Funboost.FunboostResultItem
  type FunboostResultsData = Api.Funboost.FunboostResultsData

  // 搜索表单
  const searchForm = ref({
    task_id: undefined,
    queue_name: undefined,
    success: undefined
  })

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
        { prop: 'task_id', label: '任务ID', width: 200 },
        { prop: 'function', label: '函数名' },
        { prop: 'queue_name', label: '队列名称' },
        { prop: 'host_name', label: '主机名' },
        { prop: 'success', label: '状态', formatter: (row) => {
          const statusConfig = getSuccessStatusConfig(row.success)
          return h(ElTag, { type: statusConfig.type }, () => statusConfig.text)
        }},
        { prop: 'time_cost', label: '耗时(s)', formatter: (row) => row.time_cost?.toFixed(2) },
        { prop: 'run_times', label: '运行次数' },
        { prop: 'insert_time', label: '插入时间', width: 160 },
        { prop: 'exception', label: '异常信息', width: 200, formatter: (row) => row.exception?.substring(0, 50) + '...' }
      ]
    },
    // 数据处理
    transform: {
      dataTransformer: (response: FunboostResultItem) => {
        // 后端返回的是 {data: [...], total: ..., page: ..., size: ..., total_pages: ...}
        return response || []
      },
      totalTransformer: (response: FunboostResultsData) => response.total || 0
    }
  })

  /**
   * 搜索处理
   */
  const handleSearch = (params: Record<string, any>) => {
    Object.assign(searchParams, params)
    getData()
  }
</script>