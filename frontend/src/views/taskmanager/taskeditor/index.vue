<template>
  <ElCard :class="[
    'flex flex-col w-full',
    isDark ? 'dark-mode' : 'light-mode'
  ]">
    <!-- 头部工具栏 -->
    <div :class="[
      'px-3 py-2 flex flex-col md:flex-row items-center justify-between gap-2 flex-shrink-0 border-b',
      isDark ? 'bg-[#252526] border-[#3e3e3e]' : 'bg-gray-50 border-gray-200'
    ]">
      <div class="flex flex-col md:flex-row items-start md:items-center gap-2 md:gap-2">
        <div class="flex flex-wrap md:flex-nowrap gap-1 md:gap-2">
          <el-button type="primary" size="small" @click="loadFilesList">
            <Refresh class="w-4 h-4" />
            刷新
          </el-button>
          <el-button size="small" @click="showCreateDialog">新建</el-button>
          <el-button size="small" @click="saveCurrentFile" :disabled="!currentFile">保存</el-button>
          <el-button size="small" @click="refreshCurrentFile" :disabled="!currentFile">重载</el-button>
        </div>
        <el-input
          v-model="searchInput"
          placeholder="搜索..."
          size="small"
          class="w-full md:w-40"
          clearable
          @input="handleSearch"
        />
      </div>

      <!-- 进程管理控件 -->
      <div class="flex-shrink-0">
        <div :class="[
          'flex flex-col md:flex-row items-center gap-2 md:gap-3 px-3 py-1 rounded transition-all',
          isDark ? 'bg-[#1e1e1e] border border-[#3e3e3e]' : 'bg-white border border-gray-200'
        ]">
          <!-- 进程状态指示器 -->
          <div class="flex items-center gap-2">
            <div :class="[
              'w-2 h-2 rounded-full animate-pulse',
              processStatus.status === 'running' ? 'bg-green-500' : 'bg-red-500'
            ]" />
            <span :class="['text-xs font-medium', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ processStatus.status === 'running' ? '运行中' : '已停止' }}
            </span>
          </div>

          <div :class="['w-full md:w-px h-px md:h-4', isDark ? 'bg-[#3e3e3e]' : 'bg-gray-200']" />

          <!-- 进程操作按钮 -->
          <el-button-group size="small">
            <el-button
              size="small"
              :type="processStatus.status === 'running' ? 'danger' : 'success'"
              :loading="processLoading.start || processLoading.stop"
              @click="toggleProcess"
            >
              {{ processStatus.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button
              size="small"
              :loading="processLoading.restart"
              @click="handleRestartProcess"
            >
              重启
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="logDialogVisible = true"
            >
              日志
            </el-button>
            <el-button
              size="small"
              :icon="RefreshIcon"
              :loading="processLoading.status"
              @click="refreshProcessStatus"
            />
          </el-button-group>
        </div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row flex-1 overflow-hidden w-full">
      <!-- 左侧文件树 -->
      <div :class="[
        'w-full md:w-64 flex flex-col flex-shrink-0 overflow-hidden border-b md:border-b-0 md:border-r',
        isDark ? 'bg-[#252526] border-[#3e3e3e]' : 'bg-gray-50 border-gray-200'
      ]">
        <div :class="[
          'px-3 py-2 flex justify-between items-center text-xs font-semibold flex-shrink-0 h-10 border-b',
          isDark ? 'bg-[#2d2d2d] border-[#3e3e3e] text-gray-200' : 'bg-white border-gray-200 text-gray-700'
        ]">
          <span>文件浏览</span>
          <el-icon 
            :class="['w-4 h-4 cursor-pointer hover:rotate-180 transition-transform duration-300', isDark ? 'text-gray-400' : 'text-gray-600']"
            @click="loadFilesList"
          >
            <Refresh />
          </el-icon>
        </div>
        <el-tree
          ref="treeRef"
          :data="filterFilesList"
          node-key="path"
          :props="{ children: 'children', label: 'name', isLeaf: 'isLeaf' }"
          :load="loadChildNodes"
          lazy
          :highlight-current="true"
          @node-click="handleNodeClick"
          :expand-on-click-node="false"
          :class="[
            'flex-1 overflow-y-auto',
            isDark ? 'tree-dark' : 'tree-light'
          ]"
        >
          <template #default="{ node, data }">
            <div class="flex items-center gap-2 w-full text-xs">
              <el-icon :class="data.type === 'directory' ? 'text-yellow-500' : 'text-blue-400'">
                <Folder v-if="data.type === 'directory'" />
                <Document v-else />
              </el-icon>
              <span class="truncate">{{ data.name }}</span>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 右侧编辑器 -->
      <div :class="[
        'flex-1 flex flex-col overflow-hidden',
        isDark ? 'bg-[#1e1e1e]' : 'bg-white'
      ]" style="height:calc(-210px + 100vh)">
        <div v-if="!currentFile" class="flex items-center justify-center flex-1 w-full">
          <el-empty :class="isDark ? 'text-gray-600' : 'text-gray-400'" description="选择文件开始编辑" />
        </div>
        <div v-else class="flex flex-col flex-1 w-full overflow-hidden">
          <div :class="[
            'flex items-center flex-shrink-0 border-b overflow-x-auto overflow-y-hidden',
            isDark ? 'bg-[#1e1e1e] border-[#3e3e3e]' : 'bg-gray-50 border-gray-200'
          ]"
            style="scrollbar-width: thin"
          >
            <div :class="[
              'flex items-center justify-between flex-shrink-0 px-3 h-9 gap-1 border-r border-b-2 relative transition-all whitespace-nowrap cursor-pointer text-xs font-medium',
              isDark ? 'bg-[#1e1e1e] text-gray-300 border-[#3e3e3e] border-b-blue-500' : 'bg-white text-gray-700 border-gray-200 border-b-blue-500'
            ]">
              <div class="flex items-center gap-1.5 flex-1 min-w-0">
                <el-icon :class="['text-sm flex-shrink-0', isDark ? 'text-gray-400' : 'text-gray-600']">
                  <Document />
                </el-icon>
                <span class="flex-1 min-w-0 whitespace-nowrap overflow-hidden text-ellipsis">{{ currentFile.name }}</span>
                <span v-if="isContentModified" :class="['w-1.5 h-1.5 rounded-full flex-shrink-0 ml-1', isDark ? 'bg-yellow-500' : 'bg-blue-500']" title="有未保存的更改"></span>
              </div>
              <el-icon 
                :class="['w-5 h-5 flex-shrink-0 cursor-pointer opacity-60 hover:opacity-100 rounded transition-all', isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-200']"
                @click="closeFile"
              >
                <Close />
              </el-icon>
            </div>
          </div>
          <div
            id="monaco-editor"
            ref="editorContainer"
            class="flex-1 w-full overflow-hidden"
            v-loading="fileLoading"
            element-loading-text="加载文件中..."
          />
        </div>
      </div>
    </div>

    <!-- 创建文件/文件夹对话框 -->
    <el-dialog v-model="createDialogVisible" title="新建文件/文件夹" width="400px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="createForm.name" placeholder="输入名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="createForm.type">
            <el-option label="文件" value="file" />
            <el-option label="文件夹" value="directory" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createFileOrDir">创建</el-button>
      </template>
    </el-dialog>

    <!-- 日志弹窗 -->
    <LogDialog v-model="logDialogVisible" />
  </ElCard>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Close, Folder, Document } from '@element-plus/icons-vue'
import { useSettingStore } from '@/store/modules/setting'
import {
  fetchListFiles,
  fetchReadFile,
  fetchWriteFile,
  fetchCreateFile,
  fetchDeleteFile
} from '@/api/files'
import { fetchStartProcess, fetchRestartProcess, fetchStopProcess, fetchGetProcessStatus } from '@/api/system-manage'
import LogDialog from '@/components/LogDialog.vue'

const RefreshIcon = Refresh

// 动态导入Monaco编辑器
let monaco: any = null
let editor: any = null

// 获取设置store
const settingStore = useSettingStore()

// 判断是否为深色主题
const isDark = computed(() => settingStore.isDark)

// 数据
const filesList = ref<any[]>([])
const currentFile = ref<any>(null)
const currentFileContent = ref<string>('')
const isContentModified = ref(false)
const searchInput = ref<string>('')
const treeRef = ref()
let ignoreNextChange = false // 用于忽略setValue导致的修改事件

// 文件加载loading状态
const fileLoading = ref(false)

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

// 创建对话框
const createDialogVisible = ref(false)
const createForm = reactive({
  name: '',
  type: 'file'
})

// 日志弹窗
const logDialogVisible = ref(false)

// 计算过滤后的文件列表
const filterFilesList = computed(() => {
  if (!searchInput.value) {
    return filesList.value
  }

  const search = searchInput.value.toLowerCase()
  const filterNode = (node: any): any => {
    const matched = node.name.toLowerCase().includes(search)
    const children = node.children?.map(filterNode).filter(Boolean) || []

    if (matched || children.length > 0) {
      return {
        ...node,
        children: children.length > 0 ? children : node.children
      }
    }
    return null
  }

  return filesList.value.map(filterNode).filter(Boolean)
})

// 获取文件列表
const loadFilesList = async () => {
  try {
    const res = await fetchListFiles('')
    const items = res.items || []
    filesList.value = items.map((item: any) => ({
    ...item,
    isLeaf: item.type === 'file',
    children: item.type === 'directory' ? [] : undefined
    }))
  } catch (error) {
    ElMessage.error('加载文件列表失败: ' + error)
  }
}

// 加载子节点（懒加载）
const loadChildNodes = async (node: any, resolve: Function) => {
  try {
    console.log('加载子节点，节点数据:', node.data)
    const path = node.data.path
    console.log('加载子节点，节点路径:', path)
    const res = await fetchListFiles(path)
    const items = res.items || []
    const children = items.map((item: any) => ({
    ...item,
    isLeaf: item.type === 'file',
    children: item.type === 'directory' ? [] : undefined
    }))
    resolve(children)
  } catch (error) {
    console.error('加载子节点失败:', error)
    resolve([])
  }
}

// 处理节点点击
const handleNodeClick = async (node: any) => {
  if (node.type === 'file') {
    fileLoading.value = true
    try {
      await loadFile(node)
    } finally {
      fileLoading.value = false
    }
  }
}

// 加载文件内容
const loadFile = async (file: any) => {
  try {
    const res = await fetchReadFile(file.path)
    currentFile.value = file
    currentFileContent.value = res.content
    isContentModified.value = false

    // 等待DOM更新，确保编辑器容器已渲染
    await nextTick()

    // 确保编辑器已初始化
    if (!editor && monaco) {
      await initEditor()
    }

    // 获取文件扩展名用于语言检测
    const ext = file.name.split('.').pop() || ''
    const language = getLanguageFromExtension(ext)

    // 更新编辑器内容和语言
    if (editor && monaco) {
      // 设置标志，防止setValue触发修改事件
      ignoreNextChange = true
      editor.setValue(res.content)
      monaco.editor.setModelLanguage(editor.getModel()!, language)
      isContentModified.value = false
      
      // 确保编辑器正确布局和显示
      await nextTick()
      setTimeout(() => {
        editor?.layout()
      }, 0)
    } else {
      console.warn('编辑器未初始化:', { editor: !!editor, monaco: !!monaco })
    }
  } catch (error) {
    ElMessage.error('加载文件失败: ' + error)
  }
}

// 根据文件扩展名获取语言
const getLanguageFromExtension = (ext: string): string => {
  const languageMap: Record<string, string> = {
    py: 'python',
    js: 'javascript',
    ts: 'typescript',
    jsx: 'javascript',
    tsx: 'typescript',
    vue: 'html',
    html: 'html',
    css: 'css',
    scss: 'scss',
    less: 'less',
    json: 'json',
    xml: 'xml',
    sql: 'sql',
    md: 'markdown',
    yaml: 'yaml',
    yml: 'yaml',
    sh: 'shell',
    bash: 'shell',
    txt: 'plaintext'
  }
  return languageMap[ext.toLowerCase()] || 'plaintext'
}

// 保存文件
const saveCurrentFile = async () => {
  if (!currentFile.value || !editor) {
    return
  }

  try {
    const content = editor.getValue()
    await fetchWriteFile(currentFile.value.path, content)
    isContentModified.value = false
    currentFileContent.value = content
    ElMessage.success('文件保存成功')
  } catch (error) {
    ElMessage.error('文件保存失败: ' + error)
  }
}

// 重新加载文件
const refreshCurrentFile = async () => {
  if (currentFile.value) {
    await loadFile(currentFile.value)
    ElMessage.success('文件已重新加载')
  }
}

// 关闭文件
const closeFile = () => {
  if (isContentModified.value) {
    ElMessageBox.confirm('文件有未保存的内容，是否关闭？', '提示', {
      confirmButtonText: '关闭',
      cancelButtonText: '取消'
    }).then(() => {
      currentFile.value = null
      isContentModified.value = false
      // 销毁编辑器，重置编辑器实例
      if (editor) {
        editor.dispose()
        editor = null
      }
    })
  } else {
    currentFile.value = null
    isContentModified.value = false
    // 销毁编辑器，重置编辑器实例
    if (editor) {
      editor.dispose()
      editor = null
    }
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  createForm.name = ''
  createForm.type = 'file'
  createDialogVisible.value = true
}

// 创建文件或文件夹
const createFileOrDir = async () => {
  if (!createForm.name) {
    ElMessage.error('请输入名称')
    return
  }

  try {
    const path = createForm.name
    const isDir = createForm.type === 'directory'
    const res = await fetchCreateFile(path, isDir)
    ElMessage.success('创建成功')
    await loadFilesList()
  } catch (error) {
    ElMessage.error('创建失败: ' + error)
  }
}

// 刷新日志
const refreshLogs = async () => {
  try {
    const res = await fetchLogs()
    // 只显示最新的100行以优化性能
    logs.value = res.logs.slice(-100)
    // 自动滚动到底部
    await nextTick()
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
    }
  } catch (err) {
    console.error('获取日志失败', err)
  }
}

// 打开日志弹窗
const openLogDialog = () => {
  logDialogVisible.value = true
  refreshLogs()
  logInterval = setInterval(refreshLogs, 5000)
}

// 关闭日志弹窗
const closeLogDialog = () => {
  logDialogVisible.value = false
  if (logInterval) {
    clearInterval(logInterval)
    logInterval = null
  }
}

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

// 切换进程状态（启动/停止）
const toggleProcess = async () => {
  if (processStatus.value.status === 'running') {
    await handleStopProcess()
  } else {
    await handleStartProcess()
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

// 挂载编辑器
const editorContainer = ref<HTMLElement>()

// 初始化编辑器
const initEditor = async () => {
  if (editor) return // 已经初始化

  if (!editorContainer.value) {
    console.error('编辑器容器未找到')
    ElMessage.error('编辑器容器未找到')
    return
  }

  try {
    console.log('开始初始化编辑器，容器:', editorContainer.value)
    const theme = isDark.value ? 'vs-dark' : 'vs'
    editor = monaco.editor.create(editorContainer.value, {
      value: '',
      language: 'plaintext',
      theme: theme,
      fontSize: 14,
      fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
      automaticLayout: true,
      wordWrap: 'on',
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      lineNumbers: 'on',
      glyphMargin: true,
      folding: true,
      lineDecorationsWidth: 10,
      lineNumbersMinChars: 5
    })

    console.log('编辑器初始化成功:', editor)

    // 监听编辑器内容变化
    editor.onDidChangeModelContent(() => {
      if (!ignoreNextChange) {
        isContentModified.value = true
      }
      ignoreNextChange = false // 每次重置标志
    })

    // 快捷键保存（Ctrl+S）
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      saveCurrentFile()
    })
  } catch (error) {
    console.error('编辑器初始化失败:', error)
    ElMessage.error('编辑器初始化失败: ' + error)
    editor = null
  }
}

onMounted(async () => {
  // 动态导入Monaco
  if (!monaco) {
    try {
      monaco = await import('monaco-editor')
      console.log('Monaco加载成功')
    } catch (error) {
      console.error('Monaco导入失败:', error)
      ElMessage.error('编辑器加载失败')
      return
    }
  }

  // 等待DOM更新完成
  await nextTick()

  // 加载文件列表
  loadFilesList()

  // 加载进程状态
  refreshProcessStatus()

  // 监听窗口大小变化，自动调整编辑器大小
  const resizeHandler = () => {
    if (editor) {
      editor.layout()
    }
  }
  window.addEventListener('resize', resizeHandler)

  // 监听主题变化，更新编辑器主题
  const unwatch = watch(isDark, (newVal) => {
    if (editor && monaco) {
      const newTheme = newVal ? 'vs-dark' : 'vs'
      monaco.editor.setTheme(newTheme)
    }
  })

  // 返回清理函数用于卸载
  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeHandler)
    unwatch()
  })
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
    editor = null
  }
})
</script>

<style scoped lang="scss">
.dark-mode {
  :deep(.el-card__body) {
    @apply flex flex-col flex-1;
  }

  :deep(.el-tree) {
    @apply bg-transparent text-gray-300 py-2;

    .el-tree-node__content {
      @apply h-8 hover:bg-[#3e3e3e] rounded transition-all my-0.75 mx-1.5 pr-2;

      &:hover {
        @apply translate-x-0.5;
      }
    }

    .el-tree-node.is-current > .el-tree-node__content {
      @apply bg-blue-700 text-white rounded font-medium;
    }

    .el-tree-node__label {
      @apply text-xs font-medium ml-1.5;
    }

    .el-icon {
      @apply text-base flex-shrink-0;
    }

    .el-tree-node__expand-icon {
      @apply w-5 text-center;
    }
  }
}

.light-mode {
  :deep(.el-card__body) {
    @apply flex flex-col flex-1;
  }

  :deep(.el-tree) {
    @apply bg-white text-gray-900 py-2;

    .el-tree-node__content {
      @apply h-8 hover:bg-gray-100 rounded transition-all my-0.75 mx-1.5 pr-2;

      &:hover {
        @apply translate-x-0.5;
      }
    }

    .el-tree-node.is-current > .el-tree-node__content {
      @apply bg-blue-100 text-blue-900 rounded font-medium;
    }

    .el-tree-node__label {
      @apply text-xs font-medium ml-1.5;
    }

    .el-icon {
      @apply text-base flex-shrink-0;
    }

    .el-tree-node__expand-icon {
      @apply w-5 text-center;
    }
  }
}

.tree-dark {
  @apply bg-transparent text-gray-300;
}

.tree-light {
  @apply bg-white text-gray-900;
}
</style>
