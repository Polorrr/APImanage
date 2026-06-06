-- AI 成本管理平台 — 数据库初始化
-- Docker MySQL 启动时自动执行

-- 确保数据库存在
CREATE DATABASE IF NOT EXISTS llm_cost
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 确保用户权限
CREATE USER IF NOT EXISTS 'llm_cost'@'%' IDENTIFIED BY 'llm_cost123';
GRANT ALL PRIVILEGES ON llm_cost.* TO 'llm_cost'@'%';
FLUSH PRIVILEGES;

USE llm_cost;

-- 设置时区
SET GLOBAL time_zone = '+08:00';
