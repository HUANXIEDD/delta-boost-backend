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
│   ├── booster.py        # BoosterCreate/Update/Login/Response/SwitchStatus
│   ├── booster_price.py # BoosterPriceCreate/Update/Response
│   ├── customer.py       # CustomerCreate/Login/Response
│   ├── order.py          # OrderCreate/StatusUpdate/Confirm/Response
│   ├── review.py         # ReviewCreate/Reply/Response
│   ├── reservation.py    # ReservationCreate/StatusUpdate/Response
│   └── shop.py           # ShopLogin/Response
├── routers/             # 路由
│   ├── shop.py           # /api/shop（空壳）
│   ├── booster.py        # /api/booster（✅ 已完成 12 个接口）
│   ├── customer.py       # /api/customer（空壳）
│   └── reservation.py    # /api/reservation（空壳）
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
| routers/booster | ✅ 完成 | 打手路由 12 个接口全部完成 |

## 当前开发进度

**下一步：完成剩余 3 个路由**

| 优先级 | 路由 | 接口数 | 说明 |
|--------|------|--------|------|
| 1 | `/api/shop` | 6 | 店家登录、审核打手、查看订单 |
| 2 | `/api/customer` | 12 | 客户注册/登录、搜索打手、下单、评价 |
| 3 | `/api/reservation` | 5 | 预约创建、查看、接受/拒绝 |

### Booster 路由已完成接口（供参考）

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /register | 注册 |
| POST | /login | 登录 |
| GET | /profile | 获取个人信息 |
| POST | /profile | 更新个人信息 |
| GET | /prices | 获取报价 |
| POST | /prices | 设置报价 |
| POST | /status | 切换忙碌状态 |
| GET | /orders | 查看我的订单 |
| POST | /orders/{order_id}/accept | 接单 |
| POST | /orders/{order_id}/reject | 拒单 |
| POST | /orders/{order_id}/complete | 完成服务 |
| GET | /reviews | 查看评价 |
| POST | /reviews/{review_id}/reply | 回复评价 |

## 已踩过的坑（避免重复犯错）

- `Depends(get_db)` 不加括号，不是 `Depends(get_db())`
- relationship 字段不加 `Mapped[...]` 类型注解，避免 IDE 报错
- 用 `order.booster_id`（外键字段）而非 `order.booster.id`（触发额外查询）
- `list[str]` 存数据库要 `json.dumps()` 转字符串
- 认证失败用 `raise HTTPException`，不是 `return HTTPException`
- 路由路径不加前缀，路由器已有 `prefix="/booster"`
- `return` 异常不会中止请求，必须用 `raise`
- 可空字段用 `str | None` 而非 `Optional[str]`
- 用户偏好用 POST 而非 PUT（认为 POST 更通用）

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
