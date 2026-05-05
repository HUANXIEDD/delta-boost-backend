# 项目文件夹结构说明

```
FastAPIProject/
├── docs/                          # 项目文档
│   └── folder-structure.md        # 本文件，说明每个文件夹和文件的用途
│
├── app/                           # 应用主目录，存放所有业务代码
│   │
│   ├── main.py                    # 【应用入口】
│   │   FastAPI 实例创建、数据库表初始化、所有路由的注册。
│   │   启动项目时运行这个文件。
│   │
│   ├── database.py                # 【数据库连接】
│   │   建立 SQLite 连接，创建 SessionLocal，供全项目复用。
│   │
│   ├── dependencies.py            # 【依赖注入】
│   │   定义 FastAPI 依赖函数，如 get_db（获取数据库会话）、
│   │   get_current_shop_owner（店家登录验证）、
│   │   get_current_booster（打手登录验证）、
│   │   get_current_customer（客户登录验证）。
│   │
│   ├── core/                      # 【核心配置】项目级别的配置和工具
│   │   ├── config.py              # 【配置】项目名称、版本、数据库路径、平台抽成比例等
│   │   └── security.py            # 【安全工具】JWT Token 生成与验证、密码哈希与校验
│   │
│   ├── models/                    # 【数据库模型】对应数据库表结构
│   │   ├── shop.py                # 店家（ShopOwner）：用户名、密码哈希
│   │   ├── booster.py              # 打手（Booster）：用户名、头像、简介、擅长服务、忙碌状态、审核状态
│   │   │                            # 打手报价（BoosterPrice）：每个打手对每种服务的单价
│   │   ├── customer.py             # 客户（Customer）：用户名、密码哈希
│   │   ├── order.py                # 订单（Order）：订单号、客户、打手、服务类型、需求描述、预算、状态、创建/完成/确认时间
│   │   ├── review.py                # 评价（Review）：关联订单、客户、打手，三维度评分（服务态度/情绪价值/局内表现）、文字内容、打手回复
│   │   └── reservation.py           # 预约（Reservation）：客户预约忙碌中的打手，服务类型、预算、状态
│   │
│   ├── schemas/                    # 【Pydantic 模型】Request / Response 的数据格式校验
│   │   ├── shop.py                # 店家的请求/响应格式
│   │   ├── booster.py             # 打手的请求/响应格式
│   │   ├── customer.py            # 客户的请求/响应格式
│   │   ├── order.py               # 订单的请求/响应格式
│   │   ├── review.py              # 评价的请求/响应格式
│   │   └── reservation.py         # 预约的请求/响应格式
│   │
│   ├── routers/                    # 【路由】接收 HTTP 请求，调用 service 层，返回响应
│   │   ├── shop.py                # 店家相关路由：登录、审核打手、查看订单
│   │   ├── booster.py             # 打手相关路由：注册、登录、个人信息、报价、接单、完成服务、评价回复
│   │   ├── customer.py            # 客户相关路由：注册、登录、浏览打手、搜索打手、下单、确认完成、评价
│   │   └── reservation.py         # 预约相关路由：创建预约、打手接受/拒绝预约
│   │
│   └── services/                    # 【业务逻辑】复杂业务逻辑在这里处理， routers 只做调度
│       ├── booster.py              # 打手相关业务：注册、报价设置、状态管理
│       ├── order.py               # 订单相关业务：创建订单、状态流转、完结逻辑
│       └── search.py              # 搜索相关业务：模糊搜索打手、按条件筛选
│
└── tests/                          # 【测试目录】
    └── __init__.py                 # 测试包标记文件
```

## 各模块依赖关系（简单说明）

```
请求进入
   ↓
routers（路由，接收参数，调用service）
   ↓
services（业务逻辑，处理复杂逻辑）
   ↓
models（数据模型，操作数据库）
   ↓
schemas（数据校验，确保输入输出格式正确）
   ↓
core（配置和安全工具，全项目共享）
```

## 下一步

每个文件的具体内容，等你确认文件夹结构没问题后，再逐个生成。
