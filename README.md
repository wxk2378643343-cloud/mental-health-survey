# 心理健康问卷分析系统

> 基于 Python（Flask）+ Vue 3 的前后端分离心理健康自测平台，支持多量表在线填写、自动评分、风险预警与可视化分析。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速启动](#快速启动)
- [内置量表](#内置量表)
- [系统截图说明](#系统截图说明)
- [API 接口](#api-接口)
- [数据库设计](#数据库设计)
- [评分逻辑](#评分逻辑)
- [安全机制](#安全机制)
- [测试](#测试)

---

## 功能特性

| 角色 | 功能 |
|------|------|
| **普通用户** | 注册/登录、在线填写量表、自动评分、查看结果解读、历史趋势图 |
| **管理员** | 数据概览统计、用户管理、测评记录查询、**创建自定义问卷**、风险预警处理 |

- 内置 4 套标准心理量表：PHQ-9、GAD-7、SDS、SAS
- 管理员可创建自定义量表，动态设置题目与评分分级
- 高风险（重度/中重度）结果自动触发预警通知
- ECharts 历史趋势折线图与管理端统计图表
- JWT 无状态认证，bcrypt 密码加密

---

## 技术栈

```
后端                         前端
──────────────────           ──────────────────────────
Flask 3.0                    Vue 3 + Vite
SQLAlchemy + SQLite          Vue Router 4
PyJWT (JWT 认证)             Pinia (状态管理)
bcrypt (密码加密)             Element Plus (UI 组件库)
Flask-CORS                   ECharts + vue-echarts
```

---

## 项目结构

```
mh-survey/
├── README.md
│
├── backend/                   # Flask 后端
│   ├── app.py                 # 应用入口 & 静态文件服务
│   ├── config.py              # 配置（密钥、DB路径）
│   ├── models.py              # SQLAlchemy ORM 模型
│   ├── scoring.py             # 量表评分引擎
│   ├── auth_utils.py          # JWT 生成/验证/装饰器
│   ├── seed.py                # 初始化量表数据 & 默认账号
│   ├── requirements.txt
│   └── routes/
│       ├── auth.py            # 认证接口（注册/登录/个人信息）
│       ├── questionnaire.py   # 量表/问卷/结果接口
│       └── admin.py           # 管理员接口（用户/统计/预警/创建问卷）
│
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── main.js            # 应用入口
│   │   ├── App.vue
│   │   ├── api/index.js       # Axios 封装
│   │   ├── store/user.js      # Pinia 用户状态
│   │   ├── router/index.js    # 路由配置
│   │   ├── assets/style.css   # 全局样式
│   │   ├── layouts/
│   │   │   ├── UserLayout.vue     # 用户端布局
│   │   │   └── AdminLayout.vue    # 管理端布局
│   │   └── views/
│   │       ├── Login.vue
│   │       ├── Register.vue
│   │       ├── user/
│   │       │   ├── Dashboard.vue  # 量表选择首页
│   │       │   ├── Survey.vue     # 问卷填写
│   │       │   ├── Result.vue     # 结果详情
│   │       │   ├── History.vue    # 历史记录 & 趋势图
│   │       │   └── Profile.vue    # 个人信息
│   │       └── admin/
│   │           ├── Dashboard.vue      # 数据概览
│   │           ├── Users.vue          # 用户管理
│   │           ├── Results.vue        # 测评记录
│   │           ├── Alerts.vue         # 风险预警
│   │           └── Questionnaires.vue # 问卷管理（创建/删除）
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── database/
│   ├── schema.sql             # 表结构文档
│   └── mh_survey.db           # SQLite 数据库（运行后自动生成）
│
├── tests/
│   └── test_api.py            # 21 个 API + 评分逻辑测试用例
│
└── docs/
    └── README.md              # 详细开发文档
```

---

## 快速启动

### 环境要求

- Python 3.9+
- Node.js 18+

### 第一步：安装后端依赖并初始化数据库

```bash
cd backend
pip install -r requirements.txt
python seed.py
```

输出示意：
```
Created admin user (admin / admin123)
Created test user (testuser / test123)
Created questionnaire: PHQ9
Created questionnaire: GAD7
Created questionnaire: SDS
Created questionnaire: SAS
Seed completed.
```

### 第二步：安装前端依赖

```bash
cd frontend
npm install
```

### 第三步A：开发模式（推荐，前后端同时运行）

```bash
# 终端1 - 后端（http://127.0.0.1:5000）
cd backend
python app.py

# 终端2 - 前端（http://localhost:3000，含热更新）
cd frontend
npm run dev
```

> Vite 已配置代理，`/api` 请求自动转发到 `:5000`，无需修改任何配置。

### 第三步B：生产模式（Flask 一体化）

```bash
# 打包前端
cd frontend && npm run build

# 启动后端（同时服务 API + 前端静态文件）
cd ../backend && python app.py
# 访问 http://127.0.0.1:5000
```

### 演示账号

系统初始化后可直接使用以下账号登录体验：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| `admin` | `admin123` | 管理员 | 可访问管理后台，查看统计、用户、预警、创建问卷 |
| `testuser` | `test123` | 普通用户 | 可填写量表、查看历史记录与趋势图 |

> 登录地址：开发模式访问 `http://localhost:3000`，生产模式访问 `http://127.0.0.1:5000`

---

## 内置量表

| 量表 | 全称 | 题数 | 计分 | 等级划分 |
|------|------|------|------|----------|
| **PHQ-9** | 患者健康问卷抑郁量表 | 9 | 原始分 0–27 | 无 / 轻度 / 中度 / 中重度 / 重度 |
| **GAD-7** | 广泛性焦虑障碍量表 | 7 | 原始分 0–21 | 无 / 轻度 / 中度 / 重度 |
| **SDS** | 抑郁自评量表（Zung） | 20 | 标准分（×1.25） | 正常 <53 / 轻度 53–62 / 中度 63–72 / 重度 >72 |
| **SAS** | 焦虑自评量表（Zung） | 20 | 标准分（×1.25） | 正常 <50 / 轻度 50–59 / 中度 60–69 / 重度 ≥70 |

---

## 系统截图说明

| 页面 | 路径 | 说明 |
|------|------|------|
| 登录/注册 | `/login` `/register` | Tab 切换，JWT 认证 |
| 用户首页 | `/user/dashboard` | 量表卡片选择，最近记录 |
| 问卷填写 | `/user/survey/:id` | 单题单选，实时进度条 |
| 结果详情 | `/user/result/:id` | 分级展示 + 文字解读 + 危机提示 |
| 历史记录 | `/user/history` | 趋势折线图 + 筛选表格 |
| 管理概览 | `/admin/dashboard` | 4项统计卡 + 趋势/饼图/柱图 |
| 问卷管理 | `/admin/questionnaires` | 创建自定义问卷，含题目编辑 |
| 风险预警 | `/admin/alerts` | 未读标记，一键全部已读 |

---

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/register` | 注册 |
| `POST` | `/api/auth/login` | 登录，返回 JWT token |
| `GET`  | `/api/auth/me` | 获取当前用户信息 |
| `PUT`  | `/api/auth/update_profile` | 更新个人信息 |

### 问卷接口（需登录）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET`  | `/api/questionnaires` | 获取全部量表列表 |
| `GET`  | `/api/questionnaires/:id` | 获取量表详情（含题目） |
| `POST` | `/api/surveys` | 开始一次新的测评 |
| `POST` | `/api/surveys/:id/submit` | 提交答案，触发自动评分 |
| `GET`  | `/api/results` | 我的历史结果列表 |
| `GET`  | `/api/results/:id` | 单条结果详情 |
| `GET`  | `/api/stats/me` | 我的历史趋势统计 |

### 管理接口（需 admin 角色）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET`  | `/api/admin/stats` | 全局统计数据 |
| `GET`  | `/api/admin/users` | 用户列表（分页/搜索） |
| `PUT`  | `/api/admin/users/:id/toggle` | 启用/禁用用户 |
| `GET`  | `/api/admin/results` | 全量测评记录 |
| `GET`  | `/api/admin/alerts` | 风险预警列表 |
| `PUT`  | `/api/admin/alerts/:id/read` | 标记单条已读 |
| `PUT`  | `/api/admin/alerts/read_all` | 全部已读 |
| `GET`  | `/api/admin/questionnaires` | 全部问卷列表 |
| `POST` | `/api/admin/questionnaires` | **创建自定义问卷** |
| `DELETE` | `/api/admin/questionnaires/:id` | 删除自定义问卷 |

---

## 数据库设计

```
users              问卷作答流程
  id               ──────────────────────────
  username         用户 → 创建 responses（一次作答）
  password(bcrypt)       → 填写 answers（每题答案）
  email / phone          → 生成 results（评分结果）
  age / gender           → 触发 alerts（高风险预警）
  role(user/admin)
  is_active

questionnaires     questions
  id  ←────────── questionnaire_id
  code(PHQ9...)    question_no
  name             content
  scoring_rules    opt_0~opt_4（选项文字）
  use_standard     reverse（是否反向计分）
```

---

## 评分逻辑

### PHQ-9 / GAD-7（0~3 分制）

```
每题原始值直接相加 → 对照分级表得出等级
```

### SDS / SAS（1~4 分制 + 标准分）

```
原始分相加 → 标准分 = round(原始分 × 1.25) → 对照分级表
反向计分题：实际得分 = 5 - 原始选项值
```

### 风险预警触发条件

等级为 `severe`（重度）或 `moderately_severe`（中重度）时，自动写入 `alerts` 表。

---

## 安全机制

- **密码存储**：bcrypt 哈希，不可逆
- **认证方式**：JWT Bearer Token，有效期 24 小时
- **权限控制**：`@login_required` / `@admin_required` 双重装饰器
- **数据隔离**：用户只能查看自己的测评结果（owner 校验）
- **输入验证**：用户名格式、密码长度、答题完整性均在后端校验

---

## 测试

```bash
python -m pytest tests/test_api.py -v
```

21 个测试用例，覆盖：
- 注册/登录/权限验证
- 量表列表与题目获取
- 问卷提交（正常/高风险/不完整）
- 管理接口权限
- PHQ-9/SDS/SAS 评分引擎（含反向计分）
