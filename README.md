<<<<<<< HEAD
# 代理池管理系统

一个高性能的代理池管理系统，支持多种代理协议（HTTP/HTTPS/SOCKS5/SOCKS4），具备自动获取、验证、测速和管理功能。

## 特性

- ✅ 支持多种代理协议：HTTP、HTTPS、SOCKS5、SOCKS4
- ✅ 自动获取代理列表
- ✅ 代理IP地理位置信息补充（支持[IPIP.net IPDB格式](https://github.com/ipipdotnet/ipdb-python)精确查询）
- ✅ 批量异步测速功能
- ✅ SQLite持久化存储
- ✅ RESTful API接口
- ✅ 定时任务自动更新
- ✅ Web界面管理
- ✅ 健康检查和监控
- ✅ 智能网络连接优化

## 安装

### 方式1：一键安装（推荐）

```bash
# 运行自动安装脚本
python install_and_run.py
```

### 方式2：手动安装

#### 1. 克隆项目

```bash
git clone <repository-url>
cd proxys
```

#### 2. 创建虚拟环境（推荐）

```bash
# 使用conda
conda create -n proxy_pool python=3.9
conda activate proxy_pool

# 或使用venv
python -m venv proxy_pool
# Windows
proxy_pool\Scripts\activate
# Linux/Mac
source proxy_pool/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量（可选）

创建 `.env` 文件：

```env
DATABASE_URL=sqlite:///proxy_pool.db
UPDATE_INTERVAL=3600
VALIDATION_INTERVAL=1800
MAX_CONCURRENT_TESTS=100
REQUEST_TIMEOUT=10
LOG_LEVEL=INFO
```

## 使用方法

### 启动服务

```bash
# 方式1：直接启动
python main.py

# 方式2：快速启动（推荐）
python start.py

# 方式3：自动安装并启动
python install_and_run.py
```

服务启动后，可以通过以下地址访问：

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

### IP地理位置功能

系统支持两种地理位置查询模式：

1. **精确模式**（推荐）：使用[IPIP.net的IPDB格式](https://github.com/ipipdotnet/ipdb-python)数据库
   - 自动下载最新的qqwry.ipdb数据库文件
   - 提供精确的国家、省份、城市、运营商信息
   - 支持经纬度、时区等详细信息

2. **内置模式**：使用预定义的IP段映射
   - 当IPDB库不可用时自动启用
   - 涵盖主要国家和地区的IP段
   - 功能完整，无需额外依赖

地理位置功能会在以下情况下自动激活：
- 添加新代理时
- 执行地理位置更新任务时
- 手动触发位置信息更新时

### API接口

#### 获取代理列表

```bash
# 获取所有代理
curl http://localhost:8000/api/proxies

# 获取HTTP代理
curl http://localhost:8000/api/proxies?protocol=HTTP

# 获取指定国家的代理
curl http://localhost:8000/api/proxies?country=中国

# 获取高速代理（响应时间小于1000ms）
curl http://localhost:8000/api/proxies?min_speed=1000

# 限制返回数量
curl http://localhost:8000/api/proxies?limit=10
```

#### 获取随机代理

```bash
curl http://localhost:8000/api/proxies/random
```

#### 添加代理

```bash
curl -X POST http://localhost:8000/api/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "HTTP",
    "host": "1.2.3.4",
    "port": 8080
  }'
```

#### 验证代理

```bash
curl -X POST http://localhost:8000/api/proxies/1/validate
```

#### 获取统计信息

```bash
curl http://localhost:8000/api/statistics
```

#### 手动更新

```bash
# 获取新代理
curl -X POST http://localhost:8000/api/update \
  -H "Content-Type: application/json" \
  -d '{"action": "fetch_new"}'

# 验证现有代理
curl -X POST http://localhost:8000/api/update \
  -H "Content-Type: application/json" \
  -d '{"action": "validate_existing"}'

# 更新地理位置
curl -X POST http://localhost:8000/api/update \
  -H "Content-Type: application/json" \
  -d '{"action": "update_location"}'
```

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   代理获取模块   │    │   代理验证模块   │    │   API服务模块   │
│                 │    │                 │    │                 │
│ - HTTP代理获取   │    │ - 连接性测试     │    │ - 获取代理接口   │
│ - HTTPS代理获取  │    │ - 速度测试       │    │ - 代理状态接口   │
│ - SOCKS代理获取  │    │ - 地理位置补充   │    │ - 统计信息接口   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────────┐
                    │   数据存储模块   │
                    │                 │
                    │ - SQLite数据库   │
                    │ - 代理信息表     │
                    │ - 测试记录表     │
                    └─────────────────┘
```

## 模块说明

### 核心模块

- **config.py**: 配置管理
- **models.py**: 数据模型定义
- **database.py**: 数据库操作
- **proxy_fetcher.py**: 代理获取
- **proxy_validator.py**: 代理验证
- **location_service.py**: 地理位置服务
- **scheduler.py**: 任务调度
- **api.py**: API接口
- **main.py**: 主程序

### 定时任务

系统会自动执行以下定时任务：

1. **获取新代理**: 每小时从指定源获取新代理
2. **验证现有代理**: 每30分钟验证现有代理的可用性
3. **更新地理位置**: 每2小时更新代理的地理位置信息
4. **清理过期记录**: 每天凌晨2点清理30天前的测试记录
5. **数据库维护**: 每周日凌晨3点删除长时间失败的代理

## 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | sqlite:///proxy_pool.db |
| UPDATE_INTERVAL | 代理更新间隔（秒） | 3600 |
| VALIDATION_INTERVAL | 代理验证间隔（秒） | 1800 |
| LOCATION_UPDATE_INTERVAL | 地理位置更新间隔（秒） | 7200 |
| MAX_CONCURRENT_TESTS | 最大并发测试数 | 100 |
| REQUEST_TIMEOUT | 请求超时时间（秒） | 10 |
| LOG_LEVEL | 日志级别 | INFO |

## 依赖库

项目依赖以下核心库：

- **FastAPI**: Web框架，提供API服务
- **uvicorn**: ASGI服务器，运行FastAPI应用
- **aiohttp**: HTTP客户端，异步代理获取和验证
- **aiosqlite**: SQLite异步库，数据库操作
- **apscheduler**: 任务调度器，定时任务管理
- **pydantic**: 数据验证，配置管理
- **requests**: HTTP请求库，基础网络操作
- **python-multipart**: 文件上传支持，API功能增强
- **ipip-ipdb**: IP地理位置查询库（可选，提供精确位置信息）

系统会自动检测ipip-ipdb库的可用性：
- 如果库可用，使用精确的IPDB格式数据库进行地理位置查询
- 如果库不可用，自动回退到内置IP段映射，功能完整无影响

## 数据库结构

### 代理信息表 (proxies)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| protocol | TEXT | 协议类型 |
| host | TEXT | IP地址 |
| port | INTEGER | 端口号 |
| username | TEXT | 用户名（可选） |
| password | TEXT | 密码（可选） |
| country | TEXT | 国家 |
| region | TEXT | 地区 |
| city | TEXT | 城市 |
| isp | TEXT | 运营商 |
| response_time | REAL | 响应时间（毫秒） |
| success_rate | REAL | 成功率 |
| last_check | TIMESTAMP | 最后检查时间 |
| status | TEXT | 状态 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 测试记录表 (test_records)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| proxy_id | INTEGER | 代理ID |
| target_url | TEXT | 测试URL |
| response_time | REAL | 响应时间 |
| status_code | INTEGER | HTTP状态码 |
| success | BOOLEAN | 是否成功 |
| error_message | TEXT | 错误信息 |
| tested_at | TIMESTAMP | 测试时间 |

## 监控和维护

### 健康检查

```bash
curl http://localhost:8000/api/health
```

### 任务状态查询

```bash
curl http://localhost:8000/api/tasks
```

### 日志查看

```bash
tail -f proxy_pool.log
```

## 部署

### 开发环境

```bash
python main.py
```

### 生产环境

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py"]
```

## 故障排除

### 常见问题

1. **代理获取失败**: 检查网络连接和代理源URL
2. **验证超时**: 调整REQUEST_TIMEOUT配置
3. **数据库锁定**: 检查并发访问情况
4. **内存占用高**: 减少MAX_CONCURRENT_TESTS值

### 日志分析

```bash
# 查看错误日志
grep ERROR proxy_pool.log

# 查看验证结果
grep "验证" proxy_pool.log

# 查看统计信息
grep "统计" proxy_pool.log
```

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持HTTP/HTTPS/SOCKS5代理
- 自动获取和验证功能
- RESTful API接口
- 定时任务调度
- 地理位置信息补充 
=======
# proxys
免费代理池


这是一个免费代理池项目，通过抓取互联网上的免费代理，构建sqlite代理池。

使用前请安装相关依赖

>>>>>>> 81296a6d5aed01c9e8dd2e37a3481a3610a55fd7
