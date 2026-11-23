# 心理健康问卷分析系统

![Flask](https://img.shields.io/badge/Flask-2563EB?style=flat-square)
![Vue 3](https://img.shields.io/badge/Vue%203-0F766E?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-334155?style=flat-square)
![JWT](https://img.shields.io/badge/JWT-B45309?style=flat-square)

## 📌 项目简介

包含在线填写问卷、自动评分、结果查询和后台管理，内置 PHQ-9、GAD-7、SDS 和 SAS 四套量表。

## 🏗️ 系统架构

- Vue 页面向 Flask 提交作答，后端负责身份验证及量表计分。
- SQLite 保存用户、问卷和提交记录。Docker 版由 Flask 一并提供页面构建产物。

## 📁 项目结构

| 路径 | 用途 |
| --- | --- |
| [`frontend`](frontend) | 作答、结果和后台界面 |
| [`backend`](backend) | API、评分相关业务及种子数据 |
| [`database`](database) | 数据库脚本 |
| [`tests`](tests) | API 测试 |
| [`docs`](docs) | 补充使用文档 |

## 🚀 如何启动

本地优先用 Docker。启动后执行初始化命令导入量表和演示账号。

### Docker 本地部署

需要 Docker 和 Compose v2。在仓库根目录创建 `.env`，填写以下变量。

```dotenv
SECRET_KEY=replace_with_a_long_random_value
APP_PORT=5000
```

```sh
docker compose config --quiet
docker compose up -d --build
docker compose exec app python seed.py
docker compose ps
```

打开 [http://localhost:5000](http://localhost:5000)，可使用前文的演示账号登录。

镜像构建 Vue 静态站点并由 Gunicorn 运行 Flask。SQLite 保存在 `survey-data` 数据卷。量表及演示账号需执行初始化命令后才会出现。仅使用虚构问卷数据。

使用 `docker compose logs --tail=100` 查看日志。使用 `docker compose down` 停止服务并保留数据卷。

### 快速启动

#### 环境要求

- Python 3.9+
- Node.js 18+

#### 第一步：安装后端依赖并初始化数据库

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

#### 第二步：安装前端依赖

```bash
cd frontend
npm install
```

#### 第三步A：开发模式（推荐，前后端同时运行）

```bash
# 终端1 - 后端（http://127.0.0.1:5000）
cd backend
python app.py

# 终端2 - 前端（http://localhost:3000，含热更新）
cd frontend
npm run dev
```

> Vite 已配置代理，`/api` 请求自动转发到 `:5000`，无需修改任何配置。

#### 第三步B：生产模式（Flask 一体化）

```bash
# 打包前端
cd frontend && npm run build

# 启动后端（同时服务 API + 前端静态文件）
cd ../backend && python app.py
# 访问 http://127.0.0.1:5000
```

#### 演示账号

系统初始化后可直接使用以下账号登录体验：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| `admin` | `admin123` | 管理员 | 可访问管理后台，查看统计、用户、预警、创建问卷 |
| `testuser` | `test123` | 普通用户 | 可填写量表、查看历史记录与趋势图 |

> 登录地址：开发模式访问 `http://localhost:3000`，生产模式访问 `http://127.0.0.1:5000`

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

---
## ✨ 核心工程亮点

1. **可扩展的通用心理量表评分引擎**：
   - 内置 PHQ-9、GAD-7、SDS、SAS 四套国际标准临床量表，统一抽象 `scoring_rules`、分制（0–3 / 1–4）、**反向计分（`5 - 原始选项`）**与**标准分换算（`round(原始分 × 1.25)`）**；
   - 支持管理员在后台动态创建自定义量表、题目与分级规则，无需改动后端代码即可扩展新测评体系。
2. **高风险自动预警与可视化追踪闭环**：测评结果命中 `severe`（重度）或 `moderately_severe`（中重度）时自动写入 `alerts` 预警中心并支持管理员已读追踪；用户端与管理端集成 ECharts 趋势折线图、饼图与柱图。
3. **严谨的认证授权与测试覆盖**：采用 bcrypt 密码哈希 + 24h JWT 无状态认证 + `@login_required` / `@admin_required` 双装饰器 + owner 级数据隔离校验；内置 21 个 Pytest 用例覆盖鉴权、提交校验与反向计分核心引擎。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源，详见根目录 [LICENSE](LICENSE) 文件。
