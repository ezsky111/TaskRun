# TaskRun

![TaskRun](https://socialify.git.ci/eventhorizonsky/TaskRun/image?description=1&font=Bitter&issues=1&language=1&logo=&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

<!-- PROJECT LOGO -->
<br />
## 项目简介

这是一个基于 Funboost 开发的 Python 任务管理程序。前后端分离架构，后端使用 FastAPI，前端使用 Vue.js。项目依赖 MySQL 和 Redis 作为中间件，用于任务队列管理和数据存储。

项目启动时，会启动子进程主动发现环境变量配置的 `/app/tasks` 目录下定义的 booster 并启动消费。`examleTask` 目录提供了示例任务代码，可作为开发自定义任务的参考。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用实例和路由注册
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证相关路由（登录接口）
│   │   ├── funboost.py      # Funboost路由
│   │   └── system.py        # 系统管理路由
│   ├── models/
│   │   ├── __init__.py
│   │   ├── funboost_result.py # Funboost结果模型
│   │   └── user.py          # 用户相关Pydantic模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── funboost_result.py # Funboost结果schema
│   ├── responses/
│   │   ├── __init__.py
│   │   └── base_response.py  # 基础响应类
│   ├── crud/
│   │   └── __init__.py      # CRUD操作（预留）
│   ├── database/
│   │   └── __init__.py      # 数据库连接配置（预留）
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py          # 认证依赖（JWT验证）
├── main.py                  # 入口点，导入app.main
├── funboost_cli_user.py
├── funboost_config.py
├── nb_log_config.py
├── requirements.txt         # Python依赖包列表
├── taskrunner.py            # 任务运行器

examleTask/                   # 示例任务目录，对应容器内 /app/tasks 路径下的代码示例
├── __init__.py
├── public.py                 # 公共函数或配置
├── task1.py                  # 示例任务1
└── task2.py                  # 示例任务2

frontend/
├── commitlint.config.cjs
├── eslint.config.mjs
├── index.html
├── LICENSE
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── public/
├── src/
│   ├── api                     # API 接口相关代码
│   │   ├── auth.ts             # 认证相关的 API 接口定义（如登录、注册、用户信息）
│   │   ├── funboost.ts         # Funboost 相关的 API 接口定义
│   │   └── system-manage.ts    # 系统管理相关的 API 接口定义（如菜单、用户、角色管理）
│   ├── App.vue                 # Vue 根组件，定义应用的全局结构和入口
│   ├── assets                  # 静态资源目录
│   │   ├── images              # 图片资源目录
│   │   │   ├── avatar/         # 头像图片
│   │   │   ├── ceremony/       # 仪式/活动图片
│   │   │   ├── common/         # 通用图片
│   │   │   ├── draw/           # 绘制图片
│   │   │   ├── lock/           # 锁定图片
│   │   │   ├── login/          # 登录图片
│   │   │   ├── settings/       # 设置图片
│   │   │   ├── svg/            # SVG 图片
│   │   │   └── user/           # 用户图片
│   │   ├── styles              # 全局样式文件
│   │   │   ├── core            # 核心样式（系统级样式）
│   │   │   ├── custom          # 自定义样式（业务级样式）
│   │   │   └── index.scss      # 样式入口文件
│   │   └── svg                 # SVG 相关资源
│   │       └── loading.ts      # 加载动画 SVG 定义
│   ├── components              # 组件目录
│   │   ├── business            # 业务组件（业务相关的自定义组件）
│   │   └── core                # 核心组件（系统级通用组件库）
│   │       ├── banners         # 横幅组件
│   │       ├── base            # 基础组件
│   │       ├── cards           # 卡片组件
│   │       ├── charts          # 图表组件
│   │       ├── forms           # 表单组件
│   │       ├── layouts         # 布局组件
│   │       └── ...             # 其他组件
│   ├── config                  # 项目配置目录
│   │   ├── assets              # 静态资源配置
│   │   ├── modules             # 模块化配置
│   │   │   ├── component.ts    # 组件配置
│   │   │   ├── fastEnter.ts    # 快捷入口配置
│   │   │   └── headerBar.ts    # 顶部栏配置
│   │   ├── index.ts            # 配置入口文件
│   │   └── setting.ts          # 系统设置配置
│   ├── directives              # Vue 自定义指令
│   │   ├── business            # 业务指令
│   │   ├── core                # 核心指令
│   │   └── index.ts            # 指令入口文件
│   ├── enums                   # 枚举定义
│   │   ├── appEnum.ts          # 应用级枚举（如主题类型、语言类型）
│   │   └── formEnum.ts         # 表单相关枚举（如表单状态、验证规则）
│   ├── env.d.ts                # TypeScript 环境声明文件
│   ├── hooks                   # Vue 3 Composable 函数（可复用逻辑）
│   │   ├── core                # 核心 Hooks
│   │   └── index.ts            # Hooks 入口文件
│   ├── locales                 # 国际化（i18n）资源
│   │   ├── index.ts            # 国际化入口文件
│   │   └── langs               # 多语言文件
│   ├── main.ts                 # 项目主入口文件
│   ├── mock                    # Mock 数据目录
│   │   ├── temp                # 临时 Mock 数据
│   │   └── upgrade             # 更新日志数据
│   ├── plugins                 # 插件配置
│   │   ├── echarts.ts          # ECharts 图表库配置
│   │   └── index.ts            # 插件入口文件
│   ├── router                  # Vue Router 路由相关代码
│   │   ├── core                # 路由核心功能
│   │   ├── guards              # 路由守卫
│   │   ├── modules             # 路由模块定义
│   │   ├── routes              # 路由配置
│   │   ├── index.ts            # 路由主入口
│   │   └── routesAlias.ts      # 路由别名定义
│   ├── store                   # Pinia 状态管理
│   │   ├── modules             # 状态管理模块
│   │   └── index.ts            # Pinia 入口文件
│   ├── types                   # TypeScript 类型定义
│   │   ├── api                 # API 相关类型
│   │   ├── common              # 通用类型定义
│   │   ├── component           # 组件相关类型
│   │   ├── config              # 配置相关类型
│   │   ├── import              # 自动导入类型声明
│   │   ├── router              # 路由相关类型
│   │   ├── store               # 状态管理相关类型
│   │   └── index.ts            # 类型定义总入口
│   ├── utils                   # 工具函数目录
│   │   ├── constants           # 常量定义
│   │   ├── form                # 表单相关工具
│   │   ├── http                # HTTP 请求工具
│   │   ├── navigation          # 导航相关工具
│   │   ├── storage             # 存储相关工具
│   │   ├── sys                 # 系统相关工具
│   │   ├── table               # 表格相关工具
│   │   ├── ui                  # UI 相关工具
│   │   ├── index.ts            # 工具函数总入口
│   │   └── router.ts           # 路由工具函数
│   └── views                   # 页面组件目录
│       ├── auth/               # 认证页面
│       ├── dashboard/          # 仪表盘页面
│       ├── exception/          # 异常页面
│       ├── index/              # 首页
│       ├── outside/            # 外部页面
│       ├── result/             # 结果页面
│       ├── system/             # 系统管理页面
│       └── taskmanager/        # 任务管理页面
```

## Docker 部署

这是一个基于funboost开发的python任务管理程序。项目依赖 MySQL 和 Redis 作为中间件。

### 1. 拉取 Docker 镜像
首先，从 GitHub Container Registry（GHCR） 拉取最新的镜像（由 CI/CD 自动构建和推送）：
```bash
docker pull ghcr.io/eventhorizonsky/taskrun:latest
```

### 2. 运行容器（基础指令）
如果不使用 docker-compose，可以直接运行容器，但需要手动启动 MySQL 和 Redis，并设置所有环境变量。以下是示例命令（假设 MySQL 和 Redis 已运行在本地或容器中）：

```bash
docker run -d \
  --name taskrun-app \
  -p 8000:8000 \
  -e SECRET_KEY="your-custom-secret-key" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="admin123" \
  -e REDIS_HOST="127.0.0.1" \
  -e REDIS_USERNAME="" \
  -e REDIS_PASSWORD="" \
  -e REDIS_PORT=6379 \
  -e REDIS_DB=7 \
  -e REDIS_DB_FILTER_AND_RPC_RESULT=8 \
  -e REDIS_SSL=False \
  -e SQLACHEMY_ENGINE_URL="mysql://root:xyztxdys@127.0.0.1:3306/test" \
  -e TASKS_DIR="/app/tasks" \
  -e LOGS_DIR="/app/logs" \
  -v /host/path/to/tasks:/app/tasks \
  -v /host/path/to/logs:/app/logs \
  ghcr.io/eventhorizonsky/taskrun:latest
```

- **说明**：
  - `-d`: 后台运行。
  - `-p 8000:8000`: 映射端口（应用在容器内监听 8000）。
  - `-e`: 设置环境变量（见下文变量含义）。
  - `-v`: 挂载卷（tasks 和 logs 目录，用于持久化数据）。
  - 容器启动后，应用将在 http://localhost:8000 运行。
  - 健康检查会每 30 秒检查 `/api/system/health` 端点。

**注意**：这种方式需要单独管理 MySQL 和 Redis（例如，使用 `docker run` 启动它们）。推荐使用 docker-compose 以简化依赖管理。

## 截图预览

**在线编辑器**
![在线编辑器](docs/img/editor.png)
**任务看板**
![任务看板](docs/img/kanban.png)
**进程日志跟踪**
![进程日志跟踪（滚动）](docs/img/logfollow.gif)
**依赖安装演示**
![依赖安装演示](docs/img/requireinstall.gif)
**任务管理页面**
![任务管理页面](docs/img/taskmanager.png)


### 3. 环境变量含义
Dockerfile 中定义的环境变量用于配置应用。以下是每个变量的含义和默认值（如果未设置）：

- **SECRET_KEY**: JWT 令牌的密钥，用于加密/解密认证令牌。默认值: `your-secret-key-here`。**必须设置为强随机字符串**（例如，使用 `openssl rand -hex 32` 生成）。
- **ADMIN_USERNAME**: 默认管理员用户名，用于登录。默认值: `admin`。
- **ADMIN_PASSWORD**: 默认管理员密码，用于登录。默认值: `admin`。
- **TASKS_DIR**: 任务文件存储目录（容器内路径）。默认值: `/app/tasks`。用于挂载卷以持久化任务数据。
- **LOGS_DIR**: 日志文件存储目录（容器内路径）。默认值: `/app/logs`。用于挂载卷以持久化日志。
- **REDIS_HOST**: Redis 服务器主机地址。默认值: `127.0.0.1`。
- **REDIS_USERNAME**: Redis 用户名（如果有认证）。默认值: 空字符串。
- **REDIS_PASSWORD**: Redis 密码（如果有认证）。默认值: 空字符串。
- **REDIS_PORT**: Redis 端口。默认值: `6379`。
- **REDIS_DB**: Redis 默认数据库编号。默认值: `7`。
- **REDIS_DB_FILTER_AND_RPC_RESULT**: Redis 用于过滤和 RPC 结果的数据库编号。默认值: `8`。
- **REDIS_SSL**: 是否启用 Redis SSL 连接。默认值: `False`（布尔值）。
- **SQLACHEMY_ENGINE_URL**: SQLAlchemy 数据库连接 URL（用于 MySQL）。默认值: `mysql://root:xyztxdys@172.17.0.1:3306/test`。格式: `mysql://user:password@host:port/database`。
- **PIP_INDEX_URL**: Pip 安装源地址（构建/镜像构建阶段使用）。默认值: `https://pypi.tuna.tsinghua.edu.cn/simple`。

请根据部署场景替换敏感变量，生产环境建议使用 Docker secrets 或 `.env` 文件管理。 

**安全建议**：
- 不要使用默认的 `SECRET_KEY`、`ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 在生产环境中。
- 使用环境变量或 Docker secrets 来传递敏感信息。

### 4. Docker Compose 写法（推荐，包括中间件）
为了简化部署，推荐使用 Docker Compose。它会自动管理应用、MySQL 和 Redis 的依赖关系。创建一个 `docker-compose.yml` 文件（放在项目根目录），内容如下：

```yaml
version: '3.8'

services:
  app:
    image: ghcr.io/eventhorizonsky/taskrun:latest
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-custom-secret-key  # 替换为强密钥
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=admin123  # 替换为强密码
      - REDIS_HOST=redis
      - REDIS_USERNAME=
      - REDIS_PASSWORD=
      - REDIS_PORT=6379
      - REDIS_DB=7
      - REDIS_DB_FILTER_AND_RPC_RESULT=8
      - REDIS_SSL=False
      - SQLACHEMY_ENGINE_URL=mysql://root:xyztxdys@mysql:3306/test  # 注意：host 改为服务名 'mysql'
      - TASKS_DIR=/app/tasks
      - LOGS_DIR=/app/logs
    depends_on:
      - mysql
      - redis
    volumes:
      - ./tasks:/app/tasks  # 本地 tasks 目录挂载到容器
      - ./logs:/app/logs    # 本地 logs 目录挂载到容器
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/system/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: xyztxdys  # 根密码，与 Dockerfile 默认匹配
      MYSQL_DATABASE: test           # 默认数据库名
    ports:
      - "3306:3306"  # 可选：暴露端口用于外部访问
    volumes:
      - mysql_data:/var/lib/mysql    # 持久化数据卷
    command: --default-authentication-plugin=mysql_native_password  # 兼容性设置

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"  # 可选：暴露端口用于外部访问
    volumes:
      - redis_data:/data  # 持久化数据卷

volumes:
  mysql_data:  # MySQL 数据持久化
  redis_data:  # Redis 数据持久化
```

**使用步骤**：
1. 确保本地有 `docker-compose.yml` 文件。
2. 创建本地目录：`mkdir tasks logs`（用于挂载卷）。
3. 运行：`docker-compose up -d`（后台启动所有服务）。
4. 停止：`docker-compose down`。
5. 查看日志：`docker-compose logs app`。

**说明**：
- **app 服务**: 基于项目镜像，设置环境变量，挂载卷。
- **mysql 服务**: 使用 MySQL 8.0 镜像，预创建数据库 `test`，密码匹配 Dockerfile 默认。
- **redis 服务**: 使用 Redis Alpine 镜像，轻量级。
- **volumes**: 定义命名卷，用于数据持久化（避免容器重启时数据丢失）。
- **depends_on**: 确保 MySQL 和 Redis 先启动。
- **healthcheck**: 继承 Dockerfile 的健康检查。

如果需要自定义（如更改端口或添加更多配置），修改 `docker-compose.yml` 即可。生产环境建议使用 `.env` 文件管理敏感变量（Docker Compose 支持 `env_file`）。

## 致谢

本项目使用了以下开源框架和库：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架，用于构建 API
- [ArtDesignPro](https://github.com/Daymychen/art-design-pro) - 前端设计框架
- [Funboost](https://github.com/ydf0509/funboost) - Python 任务队列框架，用于分布式任务管理
 - [Shiki](https://github.com/shikijs/shiki) - 代码高亮器，用于文档/前端代码渲染
 - [Monaco Editor](https://github.com/microsoft/monaco-editor) - 浏览器端代码编辑器，用于在线编辑器界面