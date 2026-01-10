import request from '@/utils/http'

/**
 * 列出目录下的文件和文件夹
 * @param path 目录路径
 * @returns 文件列表数据
 */
export function fetchListFiles(path: string = '') {
  return request.get<Api.Files.ListFilesData>({
    url: '/api/files/list',
    params: { path }
  })
}

/**
 * 读取文件内容
 * @param path 文件路径
 * @returns 文件内容数据
 */
export function fetchReadFile(path: string) {
  return request.get<Api.Files.ReadFileData>({
    url: '/api/files/read',
    params: { path }
  })
}

/**
 * 写入文件内容
 * @param params 写入参数
 * @returns 写入结果
 */
export function fetchWriteFile(params: Api.Files.WriteFileParams) {
  return request.post<Api.Files.FileOperationData>({
    url: '/api/files/write',
    data: params
  })
}

/**
 * 删除文件或目录
 * @param params 删除参数
 * @returns 删除结果
 */
export function fetchDeleteFile(params: Api.Files.DeleteFileParams) {
  return request.del<Api.Files.FileOperationData>({
    url: '/api/files/delete',
    data: params
  })
}

/**
 * 创建文件或目录
 * @param params 创建参数
 * @returns 创建结果
 */
export function fetchCreateFile(params: Api.Files.CreateFileParams) {
  return request.post<Api.Files.FileOperationData>({
    url: '/api/files/create',
    data: params
  })
}

/**
 * 重命名或移动文件/目录
 * @param params 重命名参数
 * @returns 操作结果
 */
export function fetchRenameFile(params: Api.Files.RenameFileParams) {
  return request.post<Api.Files.FileOperationData>({
    url: '/api/files/rename',
    data: params
  })
}