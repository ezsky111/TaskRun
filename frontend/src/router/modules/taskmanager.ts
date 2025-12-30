import { AppRouteRecord } from '@/types/router'

export const taskManagerRoutes: AppRouteRecord = {
  name: 'TaskManager',
  path: '/taskmanager',
  component: '/index/index',
  meta: {
    title: '任务管理',
    icon: 'ri:pie-chart-line',
    roles: ['R_SUPER', 'R_ADMIN']
  },
  children: [
    {
      path: 'querytask',
      name: 'QueryTask',
      component: '/taskmanager/querytask',
      meta: {
        title: '任务列表',
        keepAlive: true
      }
    }
  ]
}
