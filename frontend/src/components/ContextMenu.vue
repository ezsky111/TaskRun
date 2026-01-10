<template>
  <div
    v-show="visible"
    class="fixed z-50 bg-white dark:bg-[#252526] border border-gray-200 dark:border-[#454545] rounded shadow-lg py-1 min-w-[160px]"
    :style="{ left: x + 'px', top: y + 'px' }"
    @contextmenu.prevent
  >
    <div
      v-for="item in menuItems"
      :key="item.label"
      class="px-3 py-1.5 text-sm cursor-pointer hover:bg-gray-100 dark:hover:bg-[#2a2d2e] flex items-center gap-2"
      :class="[
        item.danger ? 'text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20' : 'text-gray-700 dark:text-gray-300',
        item.disabled ? 'opacity-50 cursor-not-allowed hover:bg-transparent dark:hover:bg-transparent' : ''
      ]"
      @click="!item.disabled && handleClick(item)"
    >
      <component :is="item.icon" v-if="item.icon" class="w-4 h-4" />
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { DocumentAdd, FolderAdd, Edit, Delete } from '@element-plus/icons-vue'

interface MenuItem {
  label: string
  icon: any
  action: string
  show: boolean
  danger?: boolean
  disabled?: boolean
}

const props = defineProps<{
  visible: boolean
  x: number
  y: number
  targetNode: any
}>()

const emit = defineEmits(['update:visible', 'select'])

const menuItems = computed<MenuItem[]>(() => {
  const isDir = props.targetNode?.data?.type === 'directory'
  
  return [
    { label: '新建文件', icon: DocumentAdd, action: 'new-file', show: isDir },
    { label: '新建文件夹', icon: FolderAdd, action: 'new-folder', show: isDir },
    { label: '重命名', icon: Edit, action: 'rename', show: true },
    { label: '删除', icon: Delete, action: 'delete', danger: true, show: true }
  ].filter(item => item.show)
})

const handleClick = (item: any) => {
  emit('select', item.action, props.targetNode)
  emit('update:visible', false)
}

// Click outside to close
const closeMenu = (e: MouseEvent) => {
  if (props.visible) {
    emit('update:visible', false)
  }
}

onMounted(() => {
  document.addEventListener('click', closeMenu)
  document.addEventListener('contextmenu', closeMenu) // Close on right click elsewhere
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
  document.removeEventListener('contextmenu', closeMenu)
})
</script>
