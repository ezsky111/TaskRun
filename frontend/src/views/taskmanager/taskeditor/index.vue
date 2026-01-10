<template>
  <ElCard :class="[
    'flex flex-col w-full task-editor-card',
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
          <el-button size="small" @click="() => showCreateDialog('file')">新建</el-button>
          <el-button size="small" @click="saveCurrentFile" :disabled="!currentTab">保存</el-button>
          <el-button size="small" @click="refreshCurrentFile" :disabled="!currentTab">重载</el-button>
        </div>
        <el-input
          v-model="searchInput"
          placeholder="搜索..."
          size="small"
          class="w-full md:w-40"
          clearable
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
              @click="handleInstallDependencies"
            >
              安装依赖
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
              @click="handleViewLogs"
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
          <div class="flex items-center gap-1">
            <el-icon 
              :class="['w-4 h-4 cursor-pointer hover:text-blue-500 transition-colors', isDark ? 'text-gray-400' : 'text-gray-600']"
              title="新建文件"
              @click="showCreateDialog('file')"
            >
              <DocumentAdd />
            </el-icon>
            <el-icon 
              :class="['w-4 h-4 cursor-pointer hover:text-blue-500 transition-colors', isDark ? 'text-gray-400' : 'text-gray-600']"
              title="新建文件夹"
              @click="showCreateDialog('directory')"
            >
              <FolderAdd />
            </el-icon>
            <el-icon 
              :class="['w-4 h-4 cursor-pointer hover:rotate-180 transition-transform duration-300', isDark ? 'text-gray-400' : 'text-gray-600']"
              title="刷新"
              @click="loadFilesList"
            >
              <Refresh />
            </el-icon>
          </div>
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
          draggable
          :allow-drop="allowDrop"
          :allow-drag="allowDrag"
          @node-drop="handleNodeDrop"
          @node-contextmenu="handleContextMenu"
          :class="[
            'flex-1 overflow-y-auto task-editor-tree'
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
        <div v-if="editorTabStore.tabs.length === 0" class="flex items-center justify-center flex-1 w-full">
          <el-empty :class="isDark ? 'text-gray-600' : 'text-gray-400'" description="选择文件开始编辑" />
        </div>
        <div v-else class="flex flex-col flex-1 w-full overflow-hidden">
          <!-- 标签栏 -->
          <div :class="[
            'flex items-center flex-shrink-0 border-b overflow-x-auto overflow-y-hidden',
            isDark ? 'bg-[#252526] border-[#3e3e3e]' : 'bg-gray-100 border-gray-200'
          ]"
            style="scrollbar-width: thin"
          >
            <div
              v-for="tab in editorTabStore.tabs"
              :key="tab.path"
              :class="[
                'flex items-center justify-between flex-shrink-0 px-3 h-9 gap-2 border-r relative transition-all whitespace-nowrap cursor-pointer text-xs select-none',
                isDark 
                  ? (editorTabStore.activeTabPath === tab.path ? 'bg-[#1e1e1e] text-gray-200 border-t-2 border-t-blue-500' : 'bg-[#2d2d2d] text-gray-500 border-[#3e3e3e] hover:bg-[#2a2a2a]') 
                  : (editorTabStore.activeTabPath === tab.path ? 'bg-white text-gray-800 border-t-2 border-t-blue-500' : 'bg-gray-100 text-gray-500 border-gray-200 hover:bg-gray-200')
              ]"
              @click="switchTab(tab.path)"
            >
              <div class="flex items-center gap-1.5 flex-1 min-w-0">
                <el-icon :class="['text-sm flex-shrink-0', isDark ? 'text-gray-400' : 'text-gray-600']">
                  <Document />
                </el-icon>
                <span class="flex-1 min-w-0 whitespace-nowrap overflow-hidden text-ellipsis max-w-[150px]">{{ tab.name }}</span>
                <span v-if="tab.isModified" :class="['w-2 h-2 rounded-full flex-shrink-0 ml-1', isDark ? 'bg-white' : 'bg-black']" title="有未保存的更改"></span>
              </div>
              <el-icon 
                :class="['w-4 h-4 flex-shrink-0 cursor-pointer opacity-60 hover:opacity-100 rounded transition-all p-0.5', isDark ? 'hover:bg-gray-600' : 'hover:bg-gray-300']"
                @click.stop="closeTab(tab.path)"
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
    <LogDialog v-model="logDialogVisible" :logType="logType" />

    <!-- 右键菜单 -->
    <ContextMenu
      v-model:visible="contextMenuVisible"
      :x="contextMenuX"
      :y="contextMenuY"
      :targetNode="contextMenuTarget"
      @select="handleContextMenuSelect"
    />
  </ElCard>
</template>

<script setup lang="ts">
import './task-editor.css'
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { shikiToMonaco } from '@shikijs/monaco'
import { createHighlighter } from 'shiki'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Close, Folder, Document, DocumentAdd, FolderAdd } from '@element-plus/icons-vue'
import { useSettingStore } from '@/store/modules/setting'
import { useEditorTabStore } from '@/store/modules/editorTab'
import {
  fetchListFiles,
  fetchReadFile,
  fetchWriteFile,
  fetchCreateFile,
  fetchDeleteFile,
  fetchRenameFile
} from '@/api/files'
import { fetchStartProcess, fetchRestartProcess, fetchStopProcess, fetchGetProcessStatus, fetchInstallDependencies } from '@/api/system-manage'
import LogDialog from '@/components/LogDialog.vue'
import ContextMenu from '@/components/ContextMenu.vue'
import loader from '@monaco-editor/loader'

const RefreshIcon = Refresh

// 动态加载Monaco编辑器
let monaco: any = null
let editor: any = null
const modelMap = new Map<string, any>() // 存储文件路径到Monaco Model的映射
const viewStateMap = new Map<string, any>() // 存储文件路径到Monaco ViewState的映射

// 获取设置store
const settingStore = useSettingStore()
const editorTabStore = useEditorTabStore()

// 判断是否为深色主题
const isDark = computed(() => settingStore.isDark)

// 数据
const filesList = ref<any[]>([])
const searchInput = ref<string>('')
const treeRef = ref()

// 当前激活的Tab
const currentTab = computed(() => editorTabStore.activeTab)

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
const logType = ref<'process' | 'install'>('process')

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuTarget = ref<any>(null)

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
    const path = node.data.path
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
    await openFile(node)
  }
}

// 打开文件（创建或切换Tab）
const openFile = async (file: any) => {
  // 保存当前Tab的ViewState
  if (editorTabStore.activeTabPath && editor) {
    viewStateMap.set(editorTabStore.activeTabPath, editor.saveViewState())
  }

  editorTabStore.openTab(file)
  
  // 如果Model已存在，直接切换
  if (modelMap.has(file.path)) {
    if (editor) {
      editor.setModel(modelMap.get(file.path))
      // 恢复ViewState
      if (viewStateMap.has(file.path)) {
        editor.restoreViewState(viewStateMap.get(file.path))
      }
      editor.focus()
    }
    return
  }

  // 否则加载内容并创建Model
  fileLoading.value = true
  try {
    const res = await fetchReadFile(file.path)
    
    // 等待DOM更新，确保编辑器容器已渲染
    await nextTick()

    // 确保编辑器已初始化
    if (!editor && monaco) {
      await initEditor()
    }

    if (monaco) {
      // 获取文件扩展名用于语言检测
      const ext = file.name.split('.').pop() || ''
      const language = getLanguageFromExtension(ext)
      
      // 创建Model
      const model = monaco.editor.createModel(res.content, language, monaco.Uri.file(file.path))
      
      // 监听内容变化
      model.onDidChangeContent(() => {
        editorTabStore.setTabModified(file.path, true)
      })

      modelMap.set(file.path, model)
      
      if (editor) {
        editor.setModel(model)
        editor.focus()
      }
    }
  } catch (error) {
    ElMessage.error('加载文件失败: ' + error)
    // 如果加载失败，关闭刚才打开的Tab
    editorTabStore.closeTab(file.path)
  } finally {
    fileLoading.value = false
  }
}

// 切换Tab
const switchTab = (path: string) => {
  if (path === editorTabStore.activeTabPath) return

  // 保存当前Tab的ViewState
  if (editorTabStore.activeTabPath && editor) {
    viewStateMap.set(editorTabStore.activeTabPath, editor.saveViewState())
  }

  editorTabStore.setActiveTab(path)
  if (modelMap.has(path) && editor) {
    editor.setModel(modelMap.get(path))
    // 恢复ViewState
    if (viewStateMap.has(path)) {
      editor.restoreViewState(viewStateMap.get(path))
    }
    editor.focus()
  }
}

// 关闭Tab
const closeTab = (path: string) => {
  const tab = editorTabStore.tabs.find(t => t.path === path)
  if (tab?.isModified) {
    ElMessageBox.confirm(`文件 ${tab.name} 有未保存的更改，确定要关闭吗？`, '提示', {
      confirmButtonText: '关闭',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      performCloseTab(path)
    }).catch(() => {})
  } else {
    performCloseTab(path)
  }
}

const performCloseTab = (path: string) => {
  // 如果关闭的是当前Tab，先保存ViewState（虽然可能没用了，但保持逻辑一致）
  // 实际上关闭了就不需要保存了
  
  editorTabStore.closeTab(path)
  // 销毁Model
  if (modelMap.has(path)) {
    modelMap.get(path).dispose()
    modelMap.delete(path)
  }
  // 清除ViewState
  if (viewStateMap.has(path)) {
    viewStateMap.delete(path)
  }

  // 如果没有Tab了，清空编辑器Model
  if (editorTabStore.tabs.length === 0 && editor) {
    editor.setModel(null)
  } else {
    // 切换到新的Active Tab
    if (editorTabStore.activeTabPath && modelMap.has(editorTabStore.activeTabPath)) {
      editor.setModel(modelMap.get(editorTabStore.activeTabPath))
      // 恢复新Tab的ViewState
      if (viewStateMap.has(editorTabStore.activeTabPath)) {
        editor.restoreViewState(viewStateMap.get(editorTabStore.activeTabPath))
      }
      editor.focus()
    }
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
    vue: 'html', // vue文件暂时用html高亮，或者注册vue语言
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
  const path = editorTabStore.activeTabPath
  if (!path || !modelMap.has(path)) return

  try {
    const model = modelMap.get(path)
    const content = model.getValue()
    await fetchWriteFile({
      path: path,
      content
    })
    editorTabStore.setTabModified(path, false)
    ElMessage.success('文件保存成功')
  } catch (error) {
    ElMessage.error('文件保存失败: ' + error)
  }
}

// 重新加载文件
const refreshCurrentFile = async () => {
  const path = editorTabStore.activeTabPath
  if (!path) return

  if (editorTabStore.activeTab?.isModified) {
    try {
      await ElMessageBox.confirm('文件有未保存的更改，重新加载将丢失这些更改，是否继续？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch {
      return
    }
  }

  // 重新读取文件内容并更新Model
  try {
    const res = await fetchReadFile(path)
    if (modelMap.has(path)) {
      const model = modelMap.get(path)
      model.setValue(res.content)
      editorTabStore.setTabModified(path, false)
      ElMessage.success('文件已重新加载')
    }
  } catch (error) {
    ElMessage.error('重载失败: ' + error)
  }
}

// 显示创建对话框
const showCreateDialog = (type: 'file' | 'directory' = 'file', parentPath: string = '') => {
  createForm.name = parentPath ? `${parentPath}/` : ''
  createForm.type = type
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
    const res = await fetchCreateFile({path:path, is_dir:isDir})
    ElMessage.success('创建成功')
    await loadFilesList()
    createDialogVisible.value = false
  } catch (error) {
    ElMessage.error('创建失败: ' + error)
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
    logType.value = 'process'
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
    logType.value = 'process'
    logDialogVisible.value = true
    await refreshProcessStatus()
  } catch (err) {
    ElMessage.error('重启失败')
  } finally {
    processLoading.value.restart = false
  }
}

// 安装依赖
const handleInstallDependencies = async () => {
  try {
    await fetchInstallDependencies()
    ElMessage.success('依赖安装已开始')
    logType.value = 'install'
    logDialogVisible.value = true
  } catch (err) {
    ElMessage.error('安装失败')
  }
}

// 查看日志
const handleViewLogs = () => {
  logType.value = 'process'
  logDialogVisible.value = true
}

// 挂载编辑器
const editorContainer = ref<HTMLElement>()

// 初始化编辑器
const initEditor = async () => {
  if (editor) return // 已经初始化
  const highlighter = await createHighlighter({
    themes: [
      'one-light',
      'one-dark-pro'
    ],
    langs: [
      'javascript',
      'typescript',
      'vue',
      'python',
      'json'
    ],
  })
  monaco.languages.register({ id: 'vue' })
  monaco.languages.register({ id: 'typescript' })
  monaco.languages.register({ id: 'javascript' })
  monaco.languages.register({ id: 'python' })

    // Register the themes from Shiki, and provide syntax highlighting for Monaco.
    shikiToMonaco(highlighter, monaco)
  if (!editorContainer.value) {
    console.error('编辑器容器未找到')
    ElMessage.error('编辑器容器未找到')
    return
  }

  try {
    console.log('开始初始化编辑器，容器:', editorContainer.value)
    const theme = isDark.value ? 'one-dark-pro' : 'one-light'
    // 创建编辑器时不指定 model，后续通过 setModel 设置
    editor = monaco.editor.create(editorContainer.value, {
      model: null,
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
    console.log('编辑器初始化完成，主题:', theme)

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

// 拖拽相关逻辑
const allowDrop = (draggingNode: any, dropNode: any, type: any) => {
  // 只允许放入文件夹中
  return dropNode.data.type === 'directory' && type === 'inner'
}

const allowDrag = (node: any) => {
  return true
}

// 处理节点拖拽
const handleNodeDrop = async (draggingNode: any, dropNode: any, dropType: any, ev: any) => {
  const oldPath = draggingNode.data.path
  const newParentPath = dropNode.data.path
  const fileName = draggingNode.data.name
  const newPath = `${newParentPath}/${fileName}`

  if (oldPath === newPath) return

  try {
    await fetchRenameFile({ old_path: oldPath, new_path: newPath })
    ElMessage.success('移动成功')
    // 刷新父节点
    loadFilesList() 
  } catch (error) {
    ElMessage.error('移动失败: ' + error)
    // 恢复树状态（这里简化处理，直接刷新）
    loadFilesList()
  }
}

// 处理右键菜单
const handleContextMenu = (event: MouseEvent, data: any, node: any, component: any) => {
  event.preventDefault()
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuTarget.value = node
  contextMenuVisible.value = true
}

// 处理菜单选择
const handleContextMenuSelect = async (action: string, node: any) => {
  const path = node.data.path
  
  switch (action) {
    case 'new-file':
      showCreateDialog('file', path)
      break
    case 'new-folder':
      showCreateDialog('directory', path)
      break
    case 'rename':
      ElMessageBox.prompt('请输入新名称', '重命名', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: node.data.name
      }).then(async ({ value }) => {
        if (!value || value === node.data.name) return
        const parentPath = path.substring(0, path.lastIndexOf('/'))
        const newPath = parentPath ? `${parentPath}/${value}` : value
        try {
          await fetchRenameFile({ old_path: path, new_path: newPath })
          ElMessage.success('重命名成功')
          loadFilesList()
        } catch (error) {
          ElMessage.error('重命名失败: ' + error)
        }
      }).catch(() => {})
      break
    case 'delete':
      ElMessageBox.confirm(`确定要删除 ${node.data.name} 吗？`, '提示', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await fetchDeleteFile({ path })
          ElMessage.success('删除成功')
          loadFilesList()
          // 如果打开了该文件，关闭它
          if (editorTabStore.tabs.find(t => t.path === path)) {
            closeTab(path)
          }
        } catch (error) {
          ElMessage.error('删除失败: ' + error)
        }
      }).catch(() => {})
      break
  }
}

onMounted(async () => {
  // 使用loader加载Monaco
  try {
    monaco = await loader.init()
    console.log('Monaco加载成功')
  } catch (error) {
    console.error('Monaco加载失败:', error)
    ElMessage.error('编辑器加载失败')
    return
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
      const newTheme = newVal ? 'one-dark-pro' : 'one-light'
      console.log('切换主题为:', newTheme)
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
  // 销毁所有Model
  modelMap.forEach(model => model.dispose())
  modelMap.clear()
})
</script>
