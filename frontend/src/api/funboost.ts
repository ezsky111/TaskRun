import request from '@/utils/http'

/**
 * 获取当前关注的项目名称
 * @returns 当前关注的项目名称
 */
export function fetchGetCareProjectName() {
  return request.get<Api.Funboost.CareProjectNameData>({
    url: '/api/funboost/get_care_project_name'
  })
}

/**
 * 设置关注的项目名称
 * @param params 设置参数
 * @returns 设置结果
 */
export function fetchSetCareProjectName(params: Api.Funboost.SetCareProjectNameParams) {
  return request.post<Api.Funboost.CareProjectNameData>({
    url: '/api/funboost/set_care_project_name',
    params
  })
}

/**
 * 获取所有项目名称列表
 * @returns 所有项目名称列表
 */
export function fetchGetAllProjectNames() {
  return request.get<Api.Funboost.AllProjectNamesData>({
    url: '/api/funboost/get_all_project_names'
  })
}

/**
 * 获取 funboost 消费结果列表
 * @param params 查询参数
 * @returns 分页结果
 */
export function fetchGetFunboostResults(params: Api.Funboost.FunboostResultsParams) {
  return request.get<Api.Funboost.FunboostResultsData>({
    url: '/api/funboost/results',
    params
  })
}

/**
 * 获取所有队列的运行信息
 * @returns 所有队列的运行信息
 */
export function fetchGetAllQueueRunInfo() {
  return request.get<Api.Funboost.AllQueuesRunInfoData>({
    url: '/api/funboost/get_all_queue_run_info'
  })
}

/**
 * 获取所有队列的配置信息
 * @returns 所有队列的配置信息
 */
export function fetchGetQueuesConfig() {
  return request.get<Api.Funboost.QueueConfigData>({
    url: '/api/funboost/get_queues_config'
  })
}

/**
 * 发布消息
 * @param params 发布参数
 * @returns 发布结果
 */
export function fetchPublishMsg(params: Api.Funboost.PublishMsgParams) {
  return request.post<Api.Funboost.RpcRespData>({
    url: '/api/funboost/publish',
    params
  })
}

/**
 * 暂停队列消费
 * @param params 暂停参数
 * @returns 暂停结果
 */
export function fetchPauseConsume(params: Api.Funboost.QueueControlParams) {
  return request.post<Api.Funboost.QueueControlData>({
    url: '/api/funboost/pause_consume',
    params
  })
}

/**
 * 恢复队列消费
 * @param params 恢复参数
 * @returns 恢复结果
 */
export function fetchResumeConsume(params: Api.Funboost.QueueControlParams) {
  return request.post<Api.Funboost.QueueControlData>({
    url: '/api/funboost/resume_consume',
    params
  })
}

/**
 * 清空队列消息
 * @param params 清空参数
 * @returns 清空结果
 */
export function fetchClearQueue(params: Api.Funboost.QueueControlParams) {
  return request.post<Api.Funboost.ClearQueueData>({
    url: '/api/funboost/clear_queue',
    params
  })
}