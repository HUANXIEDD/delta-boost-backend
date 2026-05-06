# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

三角洲行动陪玩店接单系统后端 API。使用 FastAPI + MySQL/SQLite 构建，涉及三个角色：店家、打手、客户。

## 开发模式

这是一个从零学习 FastAPI 的项目。用户是初学者，**不要直接写入代码**，而是：
1. 先讲解概念（是什么、为什么）
2. 给最小可运行示例
3. 指出哪些需要用户根据需求自己改
4. 让用户自己动手写
5. 检查用户写的代码，通过后再推进下一步

## 项目结构

```
app/
├── main.py              # FastAPI 入口，lifespan（启动时建表）、路由注册
├── database.py          # 数据库连接（SessionLocal、get_db、Base、engine）
├── dependencies.py      # 认证依赖：get_current_shop / get_current_booster / get_current_customer
├── core/
│   ├── config.py        # Settings 配置类（DATABASE_URL、SECRET_KEY 等）
│   └── security.py       # verify_password、get_password_hash、create_access_token（data: dict）、verify_token（返回 dict）
├── models/              # SQLAlchemy 模型（6个表）
│   ├── shop.py          # ShopOwner
│   ├── booster.py       # Booster + BoosterPrice
│   ├── customer.py      # Customer
│   ├── order.py          # Order（+ review 一对一）
│   ├── review.py         # Review
│   └── reservation.py   # Reservation
├── schemas/             # Pydantic 格式校验（每个模型 3-4 个 Schema）
│   ├── booster.py        # BoosterCreate/Update/Login/Response
│   ├── booster_price.py # BoosterPriceCreate/Update/Response
│   ├── customer.py       # CustomerCreate/Login/Response
│   ├── order.py          # OrderCreate/StatusUpdate/Confirm/Response
│   ├── review.py         # ReviewCreate/Reply/Response
│   ├── reservation.py    # ReservationCreate/StatusUpdate/Response
│   └── shop.py           # ShopLogin/Response
├── routers/             # 路由（业务逻辑尚未实现）
│   ├── shop.py           # /api/shop
│   ├── booster.py        # /api/booster
│   ├── customer.py       # /api/customer
│   └── reservation.py    # /api/reservation
└── services/            # 业务逻辑（空目录）
```

## 已完成的部分

| 层 | 状态 | 说明 |
|----|------|------|
| models | ✅ 完成 | 6 个 SQLAlchemy 模型，含 relationship |
| schemas | ✅ 完成 | 每个模型 3-4 个 Schema（Create/Update/Response） |
| dependencies | ✅ 完成 | 三个角色的认证依赖，get_current_user 验证 Token |
| main.py | ✅ 完成 | lifespan 建表、路由注册、uvicorn 启动 |
| 数据库配置 | ✅ 完成 | 开发用 SQLite（sqlite:///./delta_boost.db） |

## 当前开发进度

**下一步：编写路由业务逻辑（routers 层）**

设计文档：`docs/superpowers/specs/2026-05-05-delta陪玩店票务系统-design.md`

### 路由概览

| 路由 | 主要 API |
|------|---------|
| `/api/shop` | POST /login（店家登录）<br>GET /boosters（查看打手列表）<br>PUT /boosters/{id}/approve（审核通过）<br>PUT /boosters/{id}/reject（审核拒绝）<br>PUT /boosters/{id}/disable（禁用）<br>GET /orders（查看所有订单） |
| `/api/booster` | POST /register（注册）<br>POST /login（登录）<br>GET /profile（获取信息）<br>PUT /profile（完善信息）<br>GET /prices（获取报价）<br>PUT /prices（设置报价）<br>PUT /status（更新忙碌状态）<br>GET /orders（我的订单）<br>PUT /orders/{id}/accept（接单）<br>PUT /orders/{id}/reject（拒单）<br>PUT /orders/{id}/complete（完成服务）<br>GET /reviews（评价列表）<br>POST /reviews/{id}/reply（回复评价） |
| `/api/customer` | POST /register（注册）<br>POST /login（登录）<br>GET /boosters（浏览打手）<br>GET /boosters/search（模糊搜索）<br>GET /boosters/{id}（打手详情）<br>POST /orders（下单）<br>GET /orders（我的订单）<br>GET /orders/{id}（订单详情）<br>PUT /orders/{id}/confirm（确认完成）<br>PUT /orders/{id}/cancel（取消订单）<br>POST /orders/{id}/review（提交评价） |
| `/api/reservation` | POST /（创建预约）<br>GET /my（我的预约-客户）<br>GET /reservations（预约列表-打手）<br>PUT /{id}/accept（接受预约）<br>PUT /{id}/reject（拒绝预约） |

## 技术要点

- **数据库**：开发用 SQLite（`sqlite:///./delta_boost.db`），生产换 MySQL（`mysql+pymysql://...`）
- **密码哈希**：bcrypt，通过 passlib 的 CryptContext 使用
- **Token**：JWT，HS256 算法，7 天有效期，`create_access_token(data: dict)` 传入 `{"sub": 用户名, "role": 角色}`
- **平台抽成**：20%（PLATFORM_COMMISSION = 0.20）
- **支付**：当前版本预留，不接入真实支付
- **relationship**：跨文件字符串引用时，relationship 字段不加 `Mapped[...]` 类型注解，避免 IDE 报错
- **可空字段**：用 `str | None` 而非 `Optional[str]`

## 设计文档位置

- `docs/superpowers/specs/2026-05-05-delta陪玩店票务系统-design.md` — 完整数据表设计、API 路由、订单状态流转
- `docs/folder-structure.md` — 文件夹结构说明
- `docs/fastapi-tutor.md` — 引导式学习教程

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（开发）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python app/main.py

# 访问 API 文档
http://127.0.0.1:8000/docs
```
