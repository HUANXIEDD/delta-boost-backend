# 三角洲陪玩店票务系统 — 设计文档

## 1. 项目概述

- **项目名称**：三角洲陪玩店票务系统
- **项目类型**：B/S 架构后端 REST API
- **核心业务**：自营陪玩店，店主招募打手，客户下单，打手接单服务，平台抽成 20%
- **技术栈**：FastAPI + SQLite（后续可迁移 PostgreSQL）

---

## 2. 系统角色

| 角色 | 说明 |
|------|------|
| 店家/店主 | 系统管理员，管理打手、查看订单、提现结算 |
| 打手 | 提供陪玩服务，接单、完成服务、回复评价 |
| 客户/顾客 | 下单、确认服务完成、评价打手 |

---

## 3. 核心模块

### 3.1 店家模块（ShopOwner）

打手注册信息审核（通过/拒绝）
打手账号管理（启用/禁用）
订单一览（查看所有订单）
数据统计（可选，后续扩展）

### 3.2 打手模块（Booster）

打手注册（自主注册，状态待审核）
打手登录（获取 Token）
完善个人信息（头像、简介、擅长服务）
设置服务报价（每种服务类型的单价）
查看当前状态（在线/忙碌）
接单/拒单（系统推送通知后操作）
完成服务（点击"完成服务"）
查看评价列表
回复评价

### 3.3 客户模块（Customer）

客户注册/登录
浏览打手列表（支持模糊搜索打手名字）
指定打手下单（按打手唯一ID精确搜索）
提交自定义需求（选择服务类型：护航/情绪/男陪/女陪，可多选）
填写预算
查看订单状态
确认服务完成
对打手评价（三维度评分 + 文字评价）

### 3.4 预约模块（Reservation）

客户可对当前"忙碌"状态的打手进行预约
打手空闲时收到预约通知
打手可接受/拒绝预约

### 3.5 搜索模块（Search）

按打手名字模糊搜索
按打手唯一ID精确搜索
按服务类型筛选打手
按价格区间筛选打手

---

## 4. 数据表设计

### 4.1 ShopOwner（店家）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| username | VARCHAR(50) | 登录用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | DATETIME | 创建时间 |

### 4.2 Booster（打手）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| unique_id | VARCHAR(20) | 唯一ID（用户可见，如"BST001"） |
| username | VARCHAR(50) | 用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| avatar | VARCHAR(255) | 头像URL |
| bio | TEXT | 简介 |
| services | JSON | 擅长服务列表，如["护航","情绪","男陪","女陪"] |
| is_busy | BOOLEAN | 是否忙碌（默认False） |
| status | VARCHAR(20) | 状态：pending/approved/rejected/disabled |
| created_at | DATETIME | 注册时间 |

### 4.3 BoosterPrice（打手报价）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| booster_id | INTEGER FK | 关联打手 |
| service_type | VARCHAR(20) | 服务类型：护航/情绪/男陪/女陪 |
| price | DECIMAL(10,2) | 单价（每小时） |

### 4.4 Customer（客户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| username | VARCHAR(50) | 用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | DATETIME | 注册时间 |

### 4.5 Order（订单）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| order_no | VARCHAR(32) | 订单号（唯一） |
| customer_id | INTEGER FK | 关联客户 |
| booster_id | INTEGER FK | 关联打手（指定打手时） |
| services | JSON | 选中的服务类型列表 |
| requirements | TEXT | 客户自定义需求描述 |
| budget | DECIMAL(10,2) | 客户预算 |
| status | VARCHAR(20) | 状态，见下方 |
| is_reservation | BOOLEAN | 是否为预约单 |
| created_at | DATETIME | 下单时间 |
| confirmed_at | DATETIME | 客户确认完成时间 |
| completed_at | DATETIME | 打手完成时间 |

**订单状态流转：**
```
CREATED（已下单）
  → ACCEPTED（打手已接受）
    → COMPLETED（服务完成，等待客户确认）
      → CONFIRMED（客户已确认，订单结束）
    → CANCELLED（打手拒绝或客户取消）
    → EXPIRED（超时未处理）
```

### 4.6 Review（评价）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| order_id | INTEGER FK | 关联订单 |
| customer_id | INTEGER FK | 关联客户 |
| booster_id | INTEGER FK | 关联打手 |
| attitude_star | INTEGER | 服务态度 1-5 |
| emotion_star | INTEGER | 情绪价值 1-5 |
| performance_star | INTEGER | 局内表现 1-5 |
| content | TEXT | 评价内容 |
| reply | TEXT | 打手回复 |
| created_at | DATETIME | 评价时间 |

### 4.7 Reservation（预约）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| customer_id | INTEGER FK | 关联客户 |
| booster_id | INTEGER FK | 关联打手 |
| services | JSON | 预约的服务类型 |
| budget | DECIMAL(10,2) | 预约预算 |
| status | VARCHAR(20) | pending/accepted/rejected/cancelled |
| created_at | DATETIME | 预约时间 |

---

## 5. API 路由设计

### 5.1 店家路由 `/api/shop`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /login | 店家登录 |
| GET | /boosters | 查看打手列表（含审核状态） |
| PUT | /boosters/{id}/approve | 审核通过打手 |
| PUT | /boosters/{id}/reject | 审核拒绝打手 |
| PUT | /boosters/{id}/disable | 禁用打手账号 |
| GET | /orders | 查看所有订单 |

### 5.2 打手路由 `/api/booster`

| 方法   | 路径                    | 说明 |
|------|-----------------------|------|
| POST | /register             | 打手注册 |
| POST | /login                | 打手登录 |
| GET  | /profile              | 获取个人信息 |
| PUT  | /profile              | 完善个人信息 |
| GET  | /prices               | 获取我的报价 |
| POST | /updateprice          | 设置/更新报价 |
| PUT  | /status               | 更新忙碌状态（忙碌/空闲） |
| GET  | /orders               | 获取我的订单 |
| PUT  | /orders/{id}/accept   | 接受订单 |
| PUT  | /orders/{id}/reject   | 拒绝订单 |
| PUT  | /orders/{id}/complete | 完成服务 |
| GET  | /reviews              | 查看我的评价 |
| POST | /reviews/{id}/reply   | 回复评价 |

### 5.3 客户路由 `/api/customer`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /register | 客户注册 |
| POST | /login | 客户登录 |
| GET | /boosters | 浏览打手列表（支持筛选） |
| GET | /boosters/search | 模糊搜索打手（按名字或唯一ID） |
| GET | /boosters/{id} | 查看打手详情（含报价） |
| POST | /orders | 创建订单 |
| GET | /orders | 获取我的订单列表 |
| GET | /orders/{id} | 获取订单详情 |
| PUT | /orders/{id}/confirm | 确认服务完成 |
| PUT | /orders/{id}/cancel | 取消订单 |
| POST | /orders/{id}/review | 提交评价 |

### 5.4 预约路由 `/api/reservation`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | / | 创建预约（打手忙碌时） |
| GET | /my | 获取我的预约（客户视角） |
| GET | /reservations | 获取预约列表（打手视角） |
| PUT | /{id}/accept | 打手接受预约 |
| PUT | /{id}/reject | 打手拒绝预约 |

---

## 6. 搜索设计

### 模糊搜索实现

打手名字搜索：`LIKE %keyword%`（大小写不敏感）
唯一ID搜索：精确匹配 `unique_id = keyword`，未找到则提示"未找到该打手"

---

## 7. 支付设计（预留）

当前版本不接入真实支付。
订单中 `budget` 字段记录客户填写的预算，作为参考。
后续接入支付时，可在 Order 表增加 `paid_amount`（实际支付金额）、`payment_status` 等字段。
平台抽成 20% 在结算时处理，不影响订单流程。

---

## 8. 项目结构（初步）

```
FastAPIProject/
├── main.py                 # 应用入口
├── database.py             # 数据库连接与模型
├── models/                 # Pydantic 模型
│   ├── shop.py
│   ├── booster.py
│   ├── customer.py
│   ├── order.py
│   └── review.py
├── routers/               # 路由
│   ├── shop.py
│   ├── booster.py
│   ├── customer.py
│   └── reservation.py
├── services/              # 业务逻辑
│   ├── booster.py
│   ├── order.py
│   └── search.py
└── docs/superpowers/specs/
    └── 2026-05-05-delta陪玩店票务系统-design.md
```

---

## 9. 优先实现顺序

1. 数据库模型 & 基础 CRUD
2. 店家模块（审核打手）
3. 打手模块（注册、报价、接单流程）
4. 客户模块（搜索、下单）
5. 评价模块
6. 预约模块
