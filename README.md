# TaskRun

## 项目简介

这是一个基于 Funboost 开发的 Python 任务管理程序。前后端分离架构，后端使用 FastAPI，前端使用 Vue.js。项目依赖 MySQL 和 Redis 作为中间件，用于任务队列管理和数据存储。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用实例和路由注册
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证相关路由（登录接口）
│   │   └── funboost.py      # Funboost路由
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # 用户相关Pydantic模型
│   ├── schemas/
│   │   └── __init__.py      # 数据库schema（预留）
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
└── nb_log_config.py
```

## Docker 部署

这是一个基于funboost开发的python任务管理程序。项目依赖 MySQL 和 Redis 作为中间件。

### 1. 拉取 Docker 镜像
首先，从 Docker Hub 拉取最新的镜像（由 CI/CD 自动构建和推送）：
```bash
docker pull ezsky111/taskrun:latest
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
  ezsky111/taskrun:latest
```

- **说明**：
  - `-d`: 后台运行。
  - `-p 8000:8000`: 映射端口（应用在容器内监听 8000）。
  - `-e`: 设置环境变量（见下文变量含义）。
  - `-v`: 挂载卷（tasks 和 logs 目录，用于持久化数据）。
  - 容器启动后，应用将在 http://localhost:8000 运行。
  - 健康检查会每 30 秒检查 `/api/system/health` 端点。

**注意**：这种方式需要单独管理 MySQL 和 Redis（例如，使用 `docker run` 启动它们）。推荐使用 docker-compose 以简化依赖管理。

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

**安全建议**：
- 不要使用默认的 `SECRET_KEY`、`ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 在生产环境中。
- 使用环境变量或 Docker secrets 来传递敏感信息。

### 4. Docker Compose 写法（推荐，包括中间件）
为了简化部署，推荐使用 Docker Compose。它会自动管理应用、MySQL 和 Redis 的依赖关系。创建一个 `docker-compose.yml` 文件（放在项目根目录），内容如下：

```yaml
version: '3.8'

services:
  app:
    image: ezsky111/taskrun:latest
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