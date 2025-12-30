<template>
  <ElForm :model="form" inline>
    <ElFormItem label="任务ID">
      <ElInput v-model="form.task_id" placeholder="请输入任务ID" clearable />
    </ElFormItem>
    <ElFormItem label="队列名称">
      <ElInput v-model="form.queue_name" placeholder="请输入队列名称" clearable />
    </ElFormItem>
    <ElFormItem label="成功状态" class="min-w-[180px]">
      <ElSelect v-model="form.success" placeholder="请选择状态" clearable>
        <ElOption label="成功" :value="true" />
        <ElOption label="失败" :value="false" />
      </ElSelect>
    </ElFormItem>
    <ElFormItem>
      <ElButton type="primary" @click="handleSearch">搜索</ElButton>
      <ElButton @click="handleReset">重置</ElButton>
    </ElFormItem>
  </ElForm>
</template>

<script setup lang="ts">
  import { reactive } from 'vue'

  interface Props {
    modelValue: Record<string, any>
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    search: [params: Record<string, any>]
    reset: []
  }>()

  const form = reactive({ ...props.modelValue })

  const handleSearch = () => {
    emit('search', { ...form })
  }

  const handleReset = () => {
    Object.keys(form).forEach(key => {
      form[key] = undefined
    })
    emit('reset')
  }
</script>