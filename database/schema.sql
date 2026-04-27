-- 心理健康问卷分析系统 数据库结构
-- SQLite

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,               -- bcrypt hash
    email       TEXT,
    phone       TEXT,
    age         INTEGER,
    gender      TEXT CHECK(gender IN ('male','female','other')),
    role        TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user','admin')),
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 量表定义表
CREATE TABLE IF NOT EXISTS questionnaires (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE,    -- PHQ9 / GAD7 / SDS / SAS
    name            TEXT NOT NULL,
    description     TEXT,
    instructions    TEXT,
    total_items     INTEGER NOT NULL,
    scoring_rules   TEXT NOT NULL,           -- JSON: 分级规则
    use_standard    INTEGER NOT NULL DEFAULT 0, -- 是否需要换算标准分(SDS/SAS=1)
    created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 题目表
CREATE TABLE IF NOT EXISTS questions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    questionnaire_id INTEGER NOT NULL REFERENCES questionnaires(id),
    question_no      INTEGER NOT NULL,       -- 题号，从1开始
    content          TEXT NOT NULL,
    opt_0            TEXT,                   -- 选项0对应文字
    opt_1            TEXT,
    opt_2            TEXT,
    opt_3            TEXT,
    opt_4            TEXT,                   -- SDS/SAS不用
    reverse          INTEGER NOT NULL DEFAULT 0  -- 1=反向计分
);

-- 问卷作答记录（一次作答会话）
CREATE TABLE IF NOT EXISTS responses (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    questionnaire_id INTEGER NOT NULL REFERENCES questionnaires(id),
    status           TEXT NOT NULL DEFAULT 'ongoing' CHECK(status IN ('ongoing','completed')),
    started_at       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    completed_at     TEXT
);

-- 每题答案
CREATE TABLE IF NOT EXISTS answers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL REFERENCES responses(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    value       INTEGER NOT NULL   -- 原始选项值 (PHQ9/GAD7: 0-3, SDS/SAS: 1-4)
);

-- 评分结果
CREATE TABLE IF NOT EXISTS results (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id      INTEGER NOT NULL UNIQUE REFERENCES responses(id),
    user_id          INTEGER NOT NULL REFERENCES users(id),
    questionnaire_id INTEGER NOT NULL REFERENCES questionnaires(id),
    raw_score        INTEGER NOT NULL,       -- 原始总分
    std_score        REAL,                   -- 标准分 (SDS/SAS)
    level            TEXT NOT NULL,          -- none/mild/moderate/severe
    level_label      TEXT NOT NULL,          -- 无/轻度/中度/重度
    interpretation   TEXT,                  -- 文字解读
    risk_flag        INTEGER NOT NULL DEFAULT 0,  -- 1=高风险
    created_at       TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 风险预警
CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    result_id   INTEGER NOT NULL REFERENCES results(id),
    alert_type  TEXT NOT NULL DEFAULT 'high_risk',
    message     TEXT NOT NULL,
    is_read     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_responses_user ON responses(user_id);
CREATE INDEX IF NOT EXISTS idx_results_user ON results(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read, user_id);
