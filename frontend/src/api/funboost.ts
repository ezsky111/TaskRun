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