# 心理健康问卷分析系统

## 项目结构

```
mh-survey/
├── backend/               # Flask 后端
│   ├── app.py             # 应用入口
│   ├── config.py          # 配置
│   ├── models.py          # 数据库模型
│   ├── scoring.py         # 评分引擎
│   ├── auth_utils.py      # JWT 工具
│   ├── seed.py            # 初始数据
│   ├── requirements.txt
│   └── routes/
│       ├── auth.py        # 认证接口
│       ├── questionnaire.py # 量表/问卷接口
│       └── admin.py       # 管理接口
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── views/user/    # 用户端页面
│   │   ├── views/admin/   # 管理端页面
│   │   ├── layouts/       # 布局组件
│   │   ├── api/           # Axios 封装
│   │   ├── store/         # Pinia 状态管理
│   │   └── router/        # Vue Router
│   └── dist/              # 打包产物（生产部署用）
├── database/
│   ├── schema.sql         # 表结构文档
│   └── mh_survey.db       # SQLite 数据库
└── tests/
    └── test_api.py        # 接口与评分测试
```

## 快速启动

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库 & 种子数据

```bash
python seed.py
# 创建账号：admin/admin123  testuser/test123
```

### 3a. 开发模式（前后端分离）

**终端1 - 后端：**
```bash
cd backend
python app.py
# http://127.0.0.1:5000
```

**终端2 - 前端（Vite Dev Server，含热更新）：**
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

### 3b. 生产模式（Flask 直接服务）

```bash
cd frontend && npm run build   # 生成 dist/
cd ../backend && python app.py # Flask 同时提供 API + 静态文件
# 访问 http://127.0.0.1:5000
```

## 运行测试

```bash
python -m pytest tests/test_api.py -v
```

## 量表说明

| 代码  | 名称           | 题数 | 计分方式       | 等级划分 |
|-------|----------------|------|----------------|----------|
| PHQ-9 | 抑郁症筛查量表 | 9    | 原始分（0-27） | 无/轻/中/中重/重度 |
| GAD-7 | 广泛性焦虑量表 | 7    | 原始分（0-21） | 无/轻/中/重度 |
| SDS   | 抑郁自评量表   | 20   | 标准分×1.25    | 正常/<53/53-72/>72 |
| SAS   | 焦虑自评量表   | 20   | 标准分×1.25    | 正常/<50/50-69/≥70 |

## API 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| GET  | /api/questionnaires | 量表列表 |
| POST | /api/surveys | 开始一次测评 |
| POST | /api/surveys/:id/submit | 提交答案（触发评分） |
| GET  | /api/results | 我的历史结果 |
| GET  | /api/stats/me | 我的趋势统计 |
| GET  | /api/admin/stats | 管理统计（需admin） |
| GET  | /api/admin/alerts | 风险预警列表 |

## 安全机制

- 密码使用 bcrypt 哈希存储
- JWT Bearer Token 认证，24 小时过期
- 管理员路由双重校验（token + role）
- 用户只能访问自己的数据（owner 校验）
- 高风险（重度/中重度）结果自动生成预警
