# DataQuark Stock Analysis API

> 为AI Agent提供完整的A股股票分析数据的后端API服务

## 📖 项目简介

DataQuark Stock Analysis API 是一个专为智能股票分析AI Agent设计的后端服务。该API能够一次性提供分析一只A股股票所需的全部结构化数据，涵盖基本面、估值、技术面和消息面四大维度。

### 🎯 核心目标

- **数据聚合**: 整合分散的金融数据源，提供统一的API接口
- **实时数据**: 为LLM提供实时、准确的金融数据"燃料"
- **结构化输出**: 输出高度结构化的JSON数据，便于AI Agent解析和利用

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Docker (可选)

### 本地安装

1. 克隆项目
```bash
git clone <repository-url>
cd GetStockData
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 根据需要修改.env文件中的配置
```

5. 启动服务
```bash
python -m uvicorn app.main:app --reload
```

服务将在 `http://localhost:8000` 启动

### Docker 部署

1. 构建镜像
```bash
docker build -t dataquark-api .
```

2. 运行容器
```bash
docker run -p 8000:8000 dataquark-api
```

## 📊 API 文档

### 核心端点

#### 获取股票完整分析报告

```
GET /api/v1/stock/full-report?code={stock_code}
```

**参数:**
- `code`: 6位A股股票代码（必填）

**示例:**
```bash
curl "http://localhost:8000/api/v1/stock/full-report?code=600519"
```

**响应结构:**
```json
{
  "code": "600519",
  "name": "贵州茅台",
  "update_time": "2024-01-01T12:00:00",
  "fundamental_analysis": {
    "market_cap": 2500.0,
    "revenue_ttm": 1200.0,
    "net_profit_ttm": 600.0,
    "roe": 25.5,
    // ... 更多基本面数据
  },
  "valuation_analysis": {
    "pe_ratio_ttm": 35.2,
    "pb_ratio": 8.5,
    "ps_ratio": 12.3,
    // ... 更多估值数据
  },
  "technical_analysis": {
    "current_price": 1680.0,
    "price_change_percent": 2.5,
    "volume": 1500000,
    // ... 更多技术面数据
  },
  "sentiment_analysis": {
    "main_net_inflow": 50000.0,
    "concept_labels": ["白酒", "消费", "核心资产"],
    // ... 更多消息面数据
  }
}
```

### 其他端点

- `GET /`: API根路径
- `GET /health`: 健康检查
- `GET /docs`: Swagger交互式API文档
- `GET /redoc`: ReDoc API文档

## 🏗️ 架构设计

### 项目结构

```
app/
├── __init__.py
├── main.py                 # FastAPI应用和路由
├── core/
│   ├── __init__.py
│   └── config.py          # 配置管理
├── models/
│   ├── __init__.py
│   └── stock_models.py    # Pydantic数据模型
└── services/
    ├── __init__.py
    └── stock_service.py   # 业务逻辑层
tests/
├── __init__.py
└── test_api.py           # API测试
```

### 技术栈

- **Web框架**: FastAPI - 高性能、异步支持、自动API文档
- **数据源**: Akshare - 开源中文财经数据接口
- **数据验证**: Pydantic - 运行时数据验证和序列化
- **服务器**: Uvicorn - 高性能ASGI服务器
- **容器化**: Docker - 环境一致性和部署便利

### 设计原则

- **单一职责**: 路由层只负责请求处理，业务逻辑封装在服务层
- **错误处理**: 完善的异常处理机制，返回明确的错误信息
- **缓存策略**: 内存LRU缓存，减少重复数据请求
- **并发处理**: 异步获取多维度数据，提升响应速度

## 🧪 测试

运行单元测试:
```bash
pytest tests/
```

运行测试并生成覆盖率报告:
```bash
pytest --cov=app tests/
```

## 📝 开发指南

### 编码规范

- 遵循 PEP 8 规范
- 使用 `black` 进行代码格式化
- 使用 `isort` 进行import排序

### 命名约定

- 变量与函数: `snake_case`
- 类与模型: `PascalCase`
- 常量: `UPPER_SNAKE_CASE`

### 提交规范

遵循 Conventional Commits 规范:
- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `refactor:` 代码重构

## 🔧 配置说明

主要配置项（在`.env`文件中设置）:

- `HOST`: 服务器监听地址（默认: 0.0.0.0）
- `PORT`: 服务器端口（默认: 8000）
- `DEBUG`: 调试模式（默认: false）
- `CACHE_TTL`: 缓存过期时间（默认: 300秒）
- `MAX_CACHE_SIZE`: 最大缓存条目数（默认: 1000）

## 🚨 错误处理

API提供标准化的错误响应:

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 股票代码未找到
- `500 Internal Server Error`: 服务器内部错误

所有错误响应都包含`detail`字段，提供详细的错误信息。

## 📈 性能特性

- **异步处理**: 并发获取多维度数据
- **内存缓存**: LRU缓存减少重复请求
- **连接复用**: HTTP连接池优化
- **数据压缩**: 自动响应压缩

## 🔒 安全考虑

- **输入验证**: Pydantic严格验证输入数据
- **错误信息**: 不暴露内部系统信息
- **资源限制**: 缓存大小和请求超时限制

## 📊 监控与日志

- **结构化日志**: 详细的操作日志记录
- **健康检查**: `/health`端点用于服务监控
- **性能指标**: 请求响应时间和成功率

## 🛣️ 版本规划

### v1.0 (当前版本)
- ✅ 实现核心API端点
- ✅ 四大维度数据覆盖
- ✅ 内存缓存机制
- ✅ Docker化部署

### v1.1 (计划中)
- 🔄 Redis缓存支持
- 🔄 并发请求优化
- 🔄 API Key认证
- 🔄 请求速率限制

### v2.0 (远期规划)
- 🔮 港股、美股支持
- 🔮 WebSocket实时推送
- 🔮 数据订阅机制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系:

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 本服务依赖akshare库及其数据源，请确保网络连接正常且数据源可用。 