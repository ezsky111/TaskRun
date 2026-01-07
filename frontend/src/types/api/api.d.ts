/**
 * API 接口类型定义模块
 *
 * 提供所有后端接口的类型定义
 *
 * ## 主要功能
 *
 * - 通用类型（分页参数、响应结构等）
 * - 认证类型（登录、用户信息等）
 * - 系统管理类型（用户、角色等）
 * - 全局命名空间声明
 *
 * ## 使用场景
 *
 * - API 请求参数类型约束
 * - API 响应数据类型定义
 * - 接口文档类型同步
 *
 * ## 注意事项
 *
 * - 在 .vue 文件使用需要在 eslint.config.mjs 中配置 globals: { Api: 'readonly' }
 * - 使用全局命名空间，无需导入即可使用
 *
 * ## 使用方式
 *
 * ```typescript
 * const params: Api.Auth.LoginParams = { username: 'admin', password: '123456' }
 * const response: Api.Auth.UserInfo = await fetchUserInfo()
 * ```
 *
 * @module types/api/api
 * @author Art Design Pro Team
 */

declare namespace Api {
  /** 通用类型 */
  namespace Common {
    /** 分页参数 */
    interface PaginationParams {
      /** 当前页码 */
      current: number
      /** 每页条数 */
      size: number
      /** 总条数 */
      total: number
    }

    /** 通用搜索参数 */
    type CommonSearchParams = Pick<PaginationParams, 'current' | 'size'>

    /** 通用响应 */
    interface CommonResponse {
      succ: boolean
      msg: string
      data?: any
      code: number
    }

    /** 分页响应基础结构 */
    interface PaginatedResponse<T = any> {
      data: T[]
      page: number
      size: number
      total: number
    }

    /** 启用状态 */
    type EnableStatus = '1' | '2'
  }

  /** 认证类型 */
  namespace Auth {
    /** 登录参数 */
    interface LoginParams {
      username: string
      password: string
    }

    /** 登录响应 */
    interface LoginResponse {
      token: string
      refreshToken: string
    }

    /** 用户信息 */
    interface UserInfo {
      buttons: string[]
      roles: string[]
      userId: number
      username: string
      email: string
      avatar?: string
    }
  }

  /** 系统管理类型 */
  namespace SystemManage {
    /** 用户列表 */
    type UserList = Api.Common.PaginatedResponse<UserListItem>

    /** 用户列表项 */
    interface UserListItem {
      id: number
      avatar: string
      status: string
      username: string
      userGender: string
      nickName: string
      userPhone: string
      userEmail: string
      userRoles: string[]
      createBy: string
      createTime: string
      updateBy: string
      updateTime: string
    }

    /** 用户搜索参数 */
    type UserSearchParams = Partial<
      Pick<UserListItem, 'id' | 'username' | 'userGender' | 'userPhone' | 'userEmail' | 'status'> &
        Api.Common.CommonSearchParams
    >

    /** 角色列表 */
    type RoleList = Api.Common.PaginatedResponse<RoleListItem>

    /** 角色列表项 */
    interface RoleListItem {
      roleId: number
      roleName: string
      roleCode: string
      description: string
      enabled: boolean
      createTime: string
    }

    /** 角色搜索参数 */
    type RoleSearchParams = Partial<
      Pick<RoleListItem, 'roleId' | 'roleName' | 'roleCode' | 'description' | 'enabled'> &
        Api.Common.CommonSearchParams
    >

    /** 子进程状态数据 */
    interface ProcessStatusData {
      status: 'running' | 'stopped'
      pid?: number
    }
  }

  /** Funboost类型 */
  namespace Funboost {
    /** 关注项目名称数据 */
    interface CareProjectNameData {
      care_project_name: string | null
    }

    /** 设置关注项目名称参数 */
    interface SetCareProjectNameParams {
      care_project_name: string
    }

    /** 所有项目名称数据 */
    interface AllProjectNamesData {
      project_names: string[]
      count: number
    }

    /** Funboost 消费结果项 */
    interface FunboostResultItem {
      _id: string
      function?: string
      host_name?: string
      host_process?: string
      insert_minutes?: string
      insert_time: string
      insert_time_str?: string
      publish_time?: number
      publish_time_format?: string
      msg_dict?: any
      params?: any
      params_str?: string
      process_id?: number
      queue_name?: string
      result?: string
      run_times?: number
      script_name?: string
      script_name_long?: string
      success: boolean
      task_id?: string
      thread_id?: number
      time_cost?: number
      time_end?: number
      time_start?: number
      total_thread?: number
      utime?: string
      exception?: string
      rpc_result_expire_seconds?: number
      exception_type?: string
      exception_msg?: string
      rpc_chain_error_msg_dict?: string
      run_status?: string
    }

    /** Funboost 结果分页响应 */
    type FunboostResultsData =Api.Common.PaginatedResponse<FunboostResultItem>

    /** Funboost 结果查询参数 */
    interface FunboostResultsParams {
      page?: number
      size?: number
      task_id?: string
      queue_name?: string
      success?: boolean
    }

    /** 活跃消费者运行信息 */
    interface ActiveConsumerRunInfo {
      queue_name: string
      computer_name: string
      computer_ip: string
      process_id: number
      consumer_id: number
      consumer_uuid: string
      start_datetime_str: string
      start_timestamp: number
      hearbeat_datetime_str: string
      hearbeat_timestamp: number
      consuming_function: string
      code_filename: string
      unit_time_for_count: number
      last_x_s_execute_count: number
      last_x_s_execute_count_fail: number
      last_execute_task_time: number
      last_x_s_avarage_function_spend_time: number | null
      last_x_s_total_cost_time: number | null
      msg_num_in_broker: number
      current_time_for_execute_task_times_every_unit_time: number
      last_timestamp_when_has_task_in_queue: number
      total_consume_count_from_start: number
      total_consume_count_from_start_fail: number
      total_cost_time_from_start: number
      avarage_function_spend_time_from_start: number | null
    }

    /** 队列参数 */
    interface QueueParams {
      queue_name: string
      broker_kind: string
      project_name: string | null
      concurrent_mode: string
      concurrent_num: number
      qps: number | null
      is_using_rpc_mode: boolean
      consuming_function_name: string
      [key: string]: any
    }

    /** 队列参数和活跃消费者数据 */
    interface QueueParamsAndActiveConsumersData {
      queue_params: QueueParams
      active_consumers: ActiveConsumerRunInfo[]
      pause_flag: number
      msg_num_in_broker: number
      history_run_count: number | null
      history_run_fail_count: number | null
      all_consumers_last_x_s_execute_count: number
      all_consumers_last_x_s_execute_count_fail: number
      all_consumers_last_x_s_avarage_function_spend_time: number | null
      all_consumers_avarage_function_spend_time_from_start: number | null
      all_consumers_total_consume_count_from_start: number
      all_consumers_total_consume_count_from_start_fail: number
      all_consumers_last_execute_task_time: number | null
    }

    /** 所有队列运行信息数据 */
    interface AllQueuesRunInfoData {
      queues: Record<string, QueueParamsAndActiveConsumersData>
      total_count: number
    }

    /** 队列配置数据 */
    interface QueueConfigData {
      queues_config: Record<string, QueueParams>
      count: number
    }

    /** 发布消息参数 */
    interface PublishMsgParams {
      queue_name: string
      msg_body: Record<string, any>
      need_result?: boolean
      timeout?: number
    }

    /** RPC响应数据 */
    interface RpcRespData {
      task_id: string | null
      status_and_result: any | null
    }

    /** 队列控制参数 */
    interface QueueControlParams {
      queue_name: string
    }

    /** 队列控制操作响应数据 */
    interface QueueControlData {
      queue_name: string
      success: boolean
    }

    /** 清空队列响应数据 */
    interface ClearQueueData {
      queue_name: string
      success: boolean
    }
  }
}
