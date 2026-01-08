import request from '@/utils/http'
import { AppRouteRecord } from '@/types/router'

// 获取用户列表
export function fetchGetUserList(params: Api.SystemManage.UserSearchParams) {
  return request.get<Api.SystemManage.UserList>({
    url: '/api/user/list',
    params
  })
}

// 获取角色列表
export function fetchGetRoleList(params: Api.SystemManage.RoleSearchParams) {
  return request.get<Api.SystemManage.RoleList>({
    url: '/api/role/list',
    params
  })
}

// 获取菜单列表
export function fetchGetMenuList() {
  return request.get<AppRouteRecord[]>({
    url: '/api/v3/system/menus/simple'
  })
}

/**
 * 启动子进程
 * @returns 启动结果
 */
export function fetchStartProcess() {
  return request.post<Api.Common.CommonResponse>({
    url: '/api/process/start'
  })
}

/**
 * 重启子进程
 * @returns 重启结果
 */
export function fetchRestartProcess() {
  return request.post({
    url: '/api/process/restart'
  })
}

/**
 * 停止子进程
 * @returns 停止结果
 */
export function fetchStopProcess() {
  return request.post({
    url: '/api/process/stop'
  })
}

/**
 * 获取子进程状态
 * @returns 子进程状态
 */
export function fetchGetProcessStatus() {
  return request.get<Api.SystemManage.ProcessStatusData>({
    url: '/api/process/status'
  })
}

/**
 * 获取日志
 * @returns 日志列表
 */
export function fetchLogs() {
  return request.get<Api.Common.CommonResponse & { data: { logs: string[] } }>({
    url: '/api/logs'
  })
}
