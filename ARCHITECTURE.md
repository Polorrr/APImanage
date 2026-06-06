# LLM Cost Platform — 项目架构文档

> AI Agent 成本管理中间件：统一代理、精确计费、成本洞察、预算告警

## 一、产品定位

**不跟 Dify 抢「搭建」，只做「管钱 + 看清楚」。**

用户把 API 地址从「中转站」改成「你的网关」，就能获得：
- 自动追踪每次 LLM 调用的 token 和费用
- 成本可视化仪表盘（按 Agent/模型/时间拆分）
- 预算告警（花多了自动通知）
- API Key 管理（团队隔离、权限控制）

## 二、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React 18 + TypeScript | 单页应用 |
| | TailwindCSS | 样式框架 |
| | ECharts | 图表 |
| | Axios | HTTP |
| 后端 | Django 5.x + DRF | 主框架 |
| | djangorestframework-simplejwt | JWT 认证 |
| | httpx | 异步 HTTP 转发 |
| 数据库 | MySQL 8.x | 主存储 |
| | Redis | 缓存 + 限流 + Celery broker |
| 异步 | Celery + django-celery-beat | 定时任务 |
| Token | tiktoken | OpenAI 系列计数 |
| 部署 | Docker Compose | 一键启动 |
| | Nginx | 反向代理 |
| | Gunicorn | WSGI |

## 三、系统架构

```
┌──────────────────────────────────────────────────────────┐
│                      用户 / Agent                         │
│              (API 地址指向你的网关)                          │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                    Nginx (反向代理)                        │
│         路由：/api/gateway/* → 网关                        │
│         路由：/api/*        → DRF API                     │
│         路由：/*            → React 前端                    │
└──────────────┬──────────────────────┬────────────────────┘
               │                      │
               ▼                      ▼
┌──────────────────────┐  ┌───────────────────────────────┐
│   LLM Gateway        │  │   DRF API (业务)               │
│   (网关核心)          │  │                               │
│                      │  │  /api/auth/    认证             │
│  1. 验证 API Key     │  │  /api/keys/    Key 管理        │
│  2. 限流检查         │  │  /api/stats/   统计查询         │
│  3. 转发到实际 API   │  │  /api/pricing/ 价格配置         │
│  4. 记录调用日志     │  │  /api/alerts/  告警规则         │
│  5. 计算 token/费用  │  │  /api/detect/  自动检测         │
│                      │  └───────────────┬───────────────┘
└──────────┬───────────┘                  │
           │                              │
           ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│                    基础设施层                               │
│                                                          │
│   MySQL 8.x          Redis              Celery Worker    │
│   ├─ users           ├─ 限流计数器       ├─ 每小时检查预算 │
│   ├─ api_keys        ├─ Key 缓存        ├─ 聚合统计      │
│   ├─ llm_call_logs   └─ Celery broker   └─ 通知发送      │
│   ├─ model_pricing                                         │
│   ├─ providers                                             │
│   ├─ budget_rules                                          │
│   └─ alert_logs                                            │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│               外部 LLM API（中转站 / 官方）                  │
│                                                          │
│   通义千问 API    DeepSeek API    OpenAI API    ...       │
└──────────────────────────────────────────────────────────┘
```

## 四、目录结构

```
llm-cost-platform/
│
├── docker-compose.yml              # 一键启动
├── .env.example                    # 环境变量模板
├── requirements.txt                # Python 依赖
│
├── backend/                        # Django 后端
│   ├── manage.py
│   ├── config/                     # 项目配置
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py                 # 总路由
│   │   ├── celery.py               # Celery 配置
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── users/                  # 用户模块
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── gateway/                # LLM 网关（核心）
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── services.py         # token 计数、成本计算
│   │   │   ├── middleware.py       # Key 验证、限流
│   │   │   └── urls.py
│   │   │
│   │   ├── pricing/                # 价格管理
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── services.py         # 自动检测逻辑
│   │   │   └── urls.py
│   │   │
│   │   ├── stats/                  # 统计分析
│   │   │   ├── __init__.py
│   │   │   ├── views.py
│   │   │   ├── services.py         # 聚合查询
│   │   │   └── urls.py
│   │   │
│   │   └── alerts/                 # 预算告警
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── tasks.py            # Celery 任务
│   │       └── urls.py
│   │
│   └── utils/                      # 公共工具
│       ├── __init__.py
│       ├── token_counter.py        # Token 计数器
│       ├── cost_calculator.py      # 成本计算
│       ├── http_client.py          # HTTP 转发客户端
│       └── rate_limiter.py         # Redis 限流
│
├── frontend/                       # React 前端
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/                    # API 请求封装
│       │   ├── client.ts           # Axios 实例
│       │   ├── auth.ts
│       │   ├── stats.ts
│       │   ├── keys.ts
│       │   ├── pricing.ts
│       │   └── alerts.ts
│       ├── pages/                  # 页面
│       │   ├── Login.tsx
│       │   ├── Register.tsx
│       │   ├── Dashboard.tsx       # 成本仪表盘（核心页面）
│       │   ├── CallLogs.tsx        # 调用日志
│       │   ├── ApiKeys.tsx         # Key 管理
│       │   ├── Pricing.tsx         # 价格配置
│       │   ├── Detection.tsx       # 自动检测
│       │   └── Alerts.tsx          # 告警设置
│       ├── components/             # 通用组件
│       │   ├── Layout.tsx          # 侧边栏布局
│       │   ├── CostChart.tsx       # 成本趋势图
│       │   ├── ModelPieChart.tsx   # 模型分布饼图
│       │   ├── AgentBarChart.tsx   # Agent 排行柱状图
│       │   └── StatsCard.tsx       # 数据卡片
│       └── styles/
│           └── globals.css
│
├── nginx/                          # Nginx 配置
│   └── nginx.conf
│
└── scripts/                        # 脚本
    ├── init_db.sql                 # 初始化数据库
    └── seed_pricing.py             # 种子数据（内置价格表）
```

## 五、MySQL 表设计

### 5.1 users — 用户表

```sql
CREATE TABLE users (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(128) NOT NULL,
    is_active       BOOLEAN      DEFAULT TRUE,
    is_staff        BOOLEAN      DEFAULT FALSE,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.2 api_keys — API 密钥表

```sql
CREATE TABLE api_keys (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT       NOT NULL,
    name            VARCHAR(100) NOT NULL COMMENT 'Key 名称，如"生产环境"',
    key_prefix      VARCHAR(16)  NOT NULL COMMENT '前缀，用于快速查找',
    key_hash        VARCHAR(128) NOT NULL COMMENT 'SHA256 hash，不存明文',
    permissions     JSON         DEFAULT ('{"read": true, "write": true}'),
    rate_limit_rpm  INT          DEFAULT 60 COMMENT '每分钟请求数限制',
    is_active       BOOLEAN      DEFAULT TRUE,
    last_used_at    DATETIME     NULL,
    expires_at      DATETIME     NULL,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    INDEX idx_key_prefix (key_prefix),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.3 providers — 供应商/中转站配置表

```sql
CREATE TABLE providers (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT       NOT NULL,
    name            VARCHAR(100) NOT NULL COMMENT '供应商名称',
    base_url        VARCHAR(500) NOT NULL COMMENT 'API 基础地址',
    api_key_enc     TEXT         NOT NULL COMMENT '加密存储的 API Key',
    status          VARCHAR(20)  DEFAULT 'active' COMMENT 'active/disabled/error',
    detect_result   JSON         NULL COMMENT '自动检测结果',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.4 model_pricing — 模型价格表

```sql
CREATE TABLE model_pricing (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    model_keyword   VARCHAR(100) NOT NULL COMMENT '模型名关键词，如 gpt-4o',
    provider_name   VARCHAR(100) NULL COMMENT '供应商名，NULL 表示通用',
    input_price     DECIMAL(10,6) NOT NULL COMMENT '输入价格（元/千token）',
    output_price    DECIMAL(10,6) NOT NULL COMMENT '输出价格（元/千token）',
    currency        VARCHAR(3)   DEFAULT 'CNY',
    is_builtin      BOOLEAN      DEFAULT FALSE COMMENT '是否内置价格',
    user_id         BIGINT       NULL COMMENT '用户自定义价格时关联',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_keyword (model_keyword),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.5 llm_call_logs — 调用日志表（核心，数据量最大）

```sql
CREATE TABLE llm_call_logs (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id             BIGINT       NOT NULL,
    api_key_id          BIGINT       NOT NULL,
    provider_id         BIGINT       NULL,
    agent_id            VARCHAR(100) NULL COMMENT '来自请求头 X-Agent-Id',
    model               VARCHAR(100) NOT NULL,
    -- Token 数据
    input_tokens_reported   INT      NULL COMMENT '上游返回的 input tokens',
    output_tokens_reported  INT      NULL COMMENT '上游返回的 output tokens',
    input_tokens_estimated  INT      NULL COMMENT '本地估算的 input tokens',
    output_tokens_estimated INT      NULL COMMENT '本地估算的 output tokens',
    data_source         VARCHAR(20)  NOT NULL COMMENT 'provider / estimated / mixed',
    -- 费用
    cost_yuan           DECIMAL(10,6) NULL COMMENT '计算出的费用（元）',
    -- 性能
    latency_ms          INT          NULL COMMENT '响应时间（毫秒）',
    status_code         INT          NULL COMMENT 'HTTP 状态码',
    is_error            BOOLEAN      DEFAULT FALSE,
    error_message       TEXT         NULL,
    -- 时间
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_time (user_id, created_at),
    INDEX idx_agent_time (agent_id, created_at),
    INDEX idx_model (model),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (TO_DAYS(created_at)) (
    PARTITION p202606 VALUES LESS THAN (TO_DAYS('2026-07-01')),
    PARTITION p202607 VALUES LESS THAN (TO_DAYS('2026-08-01')),
    PARTITION p202608 VALUES LESS THAN (TO_DAYS('2026-09-01')),
    PARTITION pmax   VALUES LESS THAN MAXVALUE
);
```

### 5.6 budget_rules — 预算告警规则表

```sql
CREATE TABLE budget_rules (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT       NOT NULL,
    name            VARCHAR(100) NOT NULL COMMENT '规则名称',
    rule_type       VARCHAR(20)  NOT NULL COMMENT 'daily / monthly / total',
    threshold_yuan  DECIMAL(10,2) NOT NULL COMMENT '告警阈值（元）',
    alert_channel   VARCHAR(20)  NOT NULL COMMENT 'webhook / email',
    webhook_url     VARCHAR(500) NULL COMMENT '企微/钉钉 webhook 地址',
    is_active       BOOLEAN      DEFAULT TRUE,
    last_triggered  DATETIME     NULL,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5.7 alert_logs — 告警记录表

```sql
CREATE TABLE alert_logs (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_id         BIGINT       NOT NULL,
    user_id         BIGINT       NOT NULL,
    trigger_cost    DECIMAL(10,2) NOT NULL COMMENT '触发时的费用',
    threshold       DECIMAL(10,2) NOT NULL,
    channel         VARCHAR(20)  NOT NULL,
    send_status     VARCHAR(20)  DEFAULT 'sent' COMMENT 'sent / failed',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_rule_id (rule_id),
    FOREIGN KEY (rule_id) REFERENCES budget_rules(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 六、API 接口设计

### 6.1 认证

```
POST   /api/auth/register          — 注册
POST   /api/auth/login             — 登录（返回 JWT）
POST   /api/auth/refresh           — 刷新 Token
GET    /api/auth/me                — 当前用户信息
```

### 6.2 LLM 网关（核心）

```
POST   /api/gateway/v1/chat/completions      — 代理 Chat 请求
POST   /api/gateway/v1/embeddings            — 代理 Embedding 请求
GET    /api/gateway/v1/models                — 列出可用模型
```

请求示例（跟调 OpenAI 一模一样，只是换个地址）：
```
POST /api/gateway/v1/chat/completions
Authorization: Bearer sk-your-api-key

{
  "model": "deepseek-chat",
  "messages": [{"role": "user", "content": "你好"}],
  "stream": false
}

# 可选自定义 Header
X-Agent-Id: customer-service-bot    ← 标记是哪个 Agent 调的
X-Provider: xxx-api                  ← 指定用哪个中转站
```

### 6.3 API Key 管理

```
GET    /api/keys/                  — 列出我的 Key
POST   /api/keys/                  — 创建 Key
PATCH  /api/keys/{id}/             — 更新 Key（名称/权限/限流）
DELETE /api/keys/{id}/             — 吊销 Key
```

### 6.4 供应商管理

```
GET    /api/providers/             — 列出供应商
POST   /api/providers/             — 添加供应商
PATCH  /api/providers/{id}/        — 更新
DELETE /api/providers/{id}/        — 删除
POST   /api/providers/{id}/detect/ — 自动检测计费
```

### 6.5 价格管理

```
GET    /api/pricing/               — 查看价格表
POST   /api/pricing/               — 添加自定义价格
PUT    /api/pricing/{id}/          — 更新价格
DELETE /api/pricing/{id}/          — 删除
GET    /api/pricing/builtin/       — 查看内置价格库
```

### 6.6 统计分析

```
GET    /api/stats/overview         — 总览（总消耗/总调用/平均延迟）
GET    /api/stats/daily            — 每日趋势（最近30天）
GET    /api/stats/by-model         — 按模型分组
GET    /api/stats/by-agent         — 按 Agent 分组
GET    /api/stats/by-provider      — 按供应商分组
GET    /api/stats/calls            — 调用日志列表（分页+筛选）
```

### 6.7 预算告警

```
GET    /api/alerts/rules           — 列出告警规则
POST   /api/alerts/rules           — 创建规则
PUT    /api/alerts/rules/{id}/     — 更新规则
DELETE /api/alerts/rules/{id}/     — 删除规则
GET    /api/alerts/logs            — 告警历史
```

## 七、前端页面设计

### 7.1 页面清单（共 8 个页面）

```
侧边栏布局：
┌──────────┬───────────────────────────────────┐
│          │                                   │
│ 📊 概览   │         页面内容区域               │
│ 📋 调用日志│                                   │
│ 🔑 API Keys│                                 │
│ 🏪 供应商  │                                   │
│ 💰 价格配置│                                   │
│ 🔍 自动检测│                                   │
│ 🔔 告警设置│                                   │
│          │                                   │
└──────────┴───────────────────────────────────┘
```

### 7.2 Dashboard 概览页（核心页面）

```
┌─────────────────────────────────────────────────────┐
│  概览                                    [本月 ▼]    │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ 总消耗    │ │ 总调用    │ │ 平均延迟  │ │ 活跃Key │ │
│  │ ¥1,234   │ │ 12,456   │ │ 823ms    │ │ 5      │ │
│  │ ↑15%     │ │ ↑23%     │ │ ↓8%      │ │        │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                     │
│  ┌───────────────────────┐ ┌───────────────────────┐│
│  │                       │ │                       ││
│  │   每日消耗趋势（折线图） │ │   模型消耗分布（饼图）  ││
│  │                       │ │                       ││
│  └───────────────────────┘ └───────────────────────┘│
│                                                     │
│  ┌──────────────────────────────────────────────────┐│
│  │  Agent 消耗排行（柱状图）                          ││
│  │                                                  ││
│  │  客服Bot     ████████████████  ¥412              ││
│  │  文案生成     ██████████████    ¥380              ││
│  │  数据分析     ████████          ¥220              ││
│  │  翻译Agent    ██████            ¥165              ││
│  └──────────────────────────────────────────────────┘│
│                                                     │
│  ┌──────────────────────────────────────────────────┐│
│  │  最近调用（表格，前10条）                           ││
│  │  时间 | 模型 | Agent | Token | 费用 | 延迟 | 状态  ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### 7.3 调用日志页

```
┌─────────────────────────────────────────────────────┐
│  调用日志                                            │
│                                                     │
│  筛选：[模型 ▼] [Agent ▼] [日期范围] [状态 ▼]  [搜索] │
│                                                     │
│  ┌──────────────────────────────────────────────────┐│
│  │ 时间      | 模型        | Agent  | Token | 费用   ││
│  ├──────────┼────────────┼────────┼───────┼─────── ││
│  │ 15:32:01 | deepseek   | 客服   | 1.2K  | ¥0.002 ││
│  │ 15:31:58 | gpt-4o     | 文案   | 3.5K  | ¥0.12  ││
│  │ 15:31:45 | qwen-max   | 分析   | 800   | ¥0.05  ││
│  │ ...      | ...        | ...    | ...   | ...    ││
│  └──────────────────────────────────────────────────┘│
│                                                     │
│  [← 1 2 3 ... 50 →]                                │
└─────────────────────────────────────────────────────┘
```

### 7.4 自动检测页

```
┌─────────────────────────────────────────────────────┐
│  API 自动检测                                        │
│                                                     │
│  API 地址：[https://xxx-api.com/v1          ]       │
│  API Key ：[sk-****************************  ]       │
│                                                     │
│  [开始检测]                                          │
│                                                     │
│  检测结果：                                          │
│  ┌──────────────────────────────────────────────────┐│
│  │ ✅ API 连接正常                                   ││
│  │ ✅ 发现 3 个模型                                   ││
│  │ ✅ 上游返回 token 统计（精确模式）                   ││
│  │                                                  ││
│  │ 自动匹配价格：                                     ││
│  │ ┌─────────────┬──────────┬──────────┬───────────┐ ││
│  │ │ 模型         │ 输入价格  │ 输出价格  │ 状态      │ ││
│  │ ├─────────────┼──────────┼──────────┼───────────┤ ││
│  │ │ deepseek-chat│ ¥1.00   │ ¥2.00   │ ✅ 已匹配  │ ││
│  │ │ qwen-max    │ ¥20.00  │ ¥60.00  │ ✅ 已匹配  │ ││
│  │ │ gpt-4o      │ [____]  │ [____]  │ ⚠️ 手动填  │ ││
│  │ └─────────────┴──────────┴──────────┴───────────┘ ││
│  │                                                  ││
│  │ [确认保存]                                         ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## 八、核心流程详解

### 8.1 网关代理流程（最关键）

```
用户请求 → Nginx → Django Gateway View
                        │
                        ├── 1. 从 Header 取 API Key
                        ├── 2. Redis 查 Key 缓存 → 验证合法性
                        ├── 3. Redis 检查限流（滑动窗口）
                        ├── 4. 根据 model 找到对应的 provider
                        ├── 5. 转发请求到 provider.base_url
                        │      (httpx 异步请求，支持 SSE 流式)
                        ├── 6. 拿到响应
                        ├── 7. 解析 usage（有就用，没有就估算）
                        ├── 8. 查价格表算费用
                        ├── 9. 异步写入 MySQL（Celery 或 async）
                        └── 10. 返回响应给用户
```

### 8.2 Token 计数策略

```
优先级：
  1. 上游返回 usage 字段 → 直接用，标记 data_source="provider"
  2. 上游没有 usage   → 本地 tokenize，标记 data_source="estimated"
  
本地估算逻辑：
  - 请求体 messages → tiktoken 编码 → input_tokens
  - 响应体 choices → tiktoken 编码 → output_tokens
  - 不同模型用不同 tokenizer：
    OpenAI 系列 → tiktoken (cl100k_base)
    通义/DeepSeek → 大致按字符数估算（中文≈1.5字/token）
```

### 8.3 自动检测流程

```
用户输入 API 地址 + Key
        │
        ├── GET {base_url}/models → 获取模型列表
        │
        ├── 对每个模型发小请求：
        │   POST {base_url}/chat/completions
        │   {"model": "xxx", "messages": [{"role":"user","content":"1"}],
        │    "max_tokens": 1}
        │
        ├── 检查响应是否有 usage 字段
        │   有 → 标记精确模式
        │   没有 → 标记估算模式
        │
        ├── 用模型名去内置价格库匹配
        │   匹配到 → 自动填入价格
        │   没匹配 → 提示用户手动填
        │
        └── 返回检测结果 JSON
```

## 九、5-7 天开发计划

### Day 1：项目骨架 + 用户系统

```
后端：
  - Django 项目初始化
  - users app：注册/登录/JWT
  - MySQL 表初始化
  - Redis 连接

前端：
  - Vite + React + TypeScript 项目初始化
  - TailwindCSS 配置
  - 登录/注册页面
  - Layout 侧边栏组件

产出：能注册、能登录、有空白主页
```

### Day 2：LLM 网关核心

```
后端：
  - gateway app
  - API Key 生成/验证/中间件
  - 代理转发逻辑（httpx）
  - Token 计数器（tiktoken）
  - 费用计算
  - 调用日志写入 MySQL

前端：
  - API Keys 管理页面

产出：改 API 地址就能代理 LLM 调用，日志自动记录
```

### Day 3：供应商 + 价格 + 自动检测

```
后端：
  - providers app
  - model_pricing app
  - 自动检测逻辑（发探测请求）
  - 内置价格种子数据

前端：
  - 供应商管理页面
  - 价格配置页面
  - 自动检测页面（粘贴地址 → 检测 → 确认）

产出：能添加供应商、自动检测计费、管理价格
```

### Day 4：统计仪表盘

```
后端：
  - stats app
  - 聚合查询 API（按日/模型/Agent）
  - 调用日志分页查询

前端：
  - Dashboard 概览页（4 个数据卡片）
  - ECharts 折线图（每日趋势）
  - ECharts 饼图（模型分布）
  - ECharts 柱状图（Agent 排行）
  - 调用日志页面（表格+筛选+分页）

产出：能看到完整的成本可视化
```

### Day 5：预算告警 + 收尾

```
后端：
  - alerts app
  - Celery 定时任务（每小时检查预算）
  - 企微/钉钉 webhook 通知

前端：
  - 告警规则管理页面
  - 告警历史页面

产出：设定预算、超了自动告警
```

### Day 6-7：测试 + 部署 + 打磨

```
- Docker Compose 编排
- Nginx 配置
- 端到端测试
- Bug 修复
- README 文档
- 演示数据准备

产出：完整可运行的系统
```

## 十、内置价格种子数据

```python
# scripts/seed_pricing.py

BUILTIN_PRICING = [
    # OpenAI
    {"keyword": "gpt-4o",           "input": 18.0,  "output": 72.0},
    {"keyword": "gpt-4o-mini",      "input": 1.08,  "output": 4.32},
    {"keyword": "gpt-4-turbo",      "input": 72.0,  "output": 216.0},
    {"keyword": "gpt-3.5-turbo",    "input": 3.6,   "output": 10.8},
    {"keyword": "o1",               "input": 108.0, "output": 432.0},
    {"keyword": "o3-mini",          "input": 7.92,  "output": 31.68},
    
    # Anthropic
    {"keyword": "claude-3-5-sonnet", "input": 21.6, "output": 108.0},
    {"keyword": "claude-3-opus",     "input": 108.0,"output": 540.0},
    {"keyword": "claude-3-haiku",    "input": 1.8,  "output": 9.0},
    
    # DeepSeek
    {"keyword": "deepseek-chat",    "input": 1.0,  "output": 2.0},
    {"keyword": "deepseek-reasoner","input": 4.0,  "output": 16.0},
    {"keyword": "deepseek-coder",   "input": 1.0,  "output": 2.0},
    
    # 通义千问
    {"keyword": "qwen-max",         "input": 20.0, "output": 60.0},
    {"keyword": "qwen-plus",        "input": 0.8,  "output": 2.0},
    {"keyword": "qwen-turbo",       "input": 0.3,  "output": 0.6},
    {"keyword": "qwen-long",        "input": 0.5,  "output": 2.0},
    
    # 智谱
    {"keyword": "glm-4",            "input": 100.0,"output": 100.0},
    {"keyword": "glm-4-flash",      "input": 1.0,  "output": 1.0},
    {"keyword": "glm-3-turbo",      "input": 1.0,  "output": 1.0},
    
    # 百度文心
    {"keyword": "ernie-4.0",        "input": 120.0,"output": 120.0},
    {"keyword": "ernie-3.5",        "input": 8.0,  "output": 8.0},
    {"keyword": "ernie-speed",      "input": 0.0,  "output": 0.0},
    
    # MiniMax
    {"keyword": "abab6.5-chat",     "input": 10.0, "output": 30.0},
    {"keyword": "abab5.5-chat",     "input": 10.0, "output": 30.0},
    
    # 零一万物
    {"keyword": "yi-large",         "input": 6.0,  "output": 6.0},
    {"keyword": "yi-medium",        "input": 1.0,  "output": 1.0},
    
    # Moonshot
    {"keyword": "moonshot-v1-128k", "input": 60.0, "output": 60.0},
    {"keyword": "moonshot-v1-32k",  "input": 48.0, "output": 48.0},
    {"keyword": "moonshot-v1-8k",   "input": 12.0, "output": 12.0},

    # Google
    {"keyword": "gemini-2.0-flash", "input": 0.72, "output": 2.88},
    {"keyword": "gemini-1.5-pro",   "input": 25.2, "output": 75.6},
]

# 所有价格单位：元/千token（人民币）
```

## 十一、Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: llm_cost
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    command: --default-authentication-plugin=mysql_native_password

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - mysql
      - redis

  celery-worker:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    env_file:
      - .env
    depends_on:
      - mysql
      - redis

  celery-beat:
    build: ./backend
    command: celery -A config beat -l info
    volumes:
      - ./backend:/app
    env_file:
      - .env
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

volumes:
  mysql_data:
```

## 十二、环境变量

```bash
# .env.example

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

# MySQL
MYSQL_ROOT_PASSWORD=your-mysql-password
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=llm_cost
MYSQL_USER=llm_cost
MYSQL_PASSWORD=your-db-password

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=60      # 分钟
JWT_REFRESH_TOKEN_LIFETIME=7      # 天

# 告警
DEFAULT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
```

## 十三、关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 前端框架 | React + Vite | 生态成熟，ECharts 集成好 |
| 后端框架 | Django + DRF | 你指定的，且 ORM 开发快 |
| 数据库 | MySQL | 你指定的，够用 |
| HTTP 转发 | httpx | 支持异步+SSE 流式 |
| Token 计数 | tiktoken | OpenAI 官方库，最准确 |
| 图表库 | ECharts | 功能全，中文友好 |
| 认证 | JWT | 无状态，前后端分离友好 |
| 限流 | Redis 滑动窗口 | 精确且高性能 |
| 定时任务 | Celery + Beat | Django 生态标配 |
| 部署 | Docker Compose | 一键启动，5-7 天够用 |
