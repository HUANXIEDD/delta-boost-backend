# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

三角洲行动陪玩店接单系统后端 API。使用 FastAPI + MySQL 构建，涉及三个角色：店家、打手、客户。

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
├── main.py              # FastAPI 入口，路由注册（尚未创建）
├── datebase.py          # 数据库连接，注意文件名拼写错误（应为 database.py）
├── dependencies.py      # 认证依赖注入（尚未创建）
├── core/
│   ├── config.py        # 项目配置（DATABASE_URL 未填写完整）
│   └── security.py      # JWT Token + 密码哈希（已完整）
├── models/              # SQLAlchemy 模型（空目录）
├── schemas/             # Pydantic 格式校验（空目录）
├── routers/              # 路由（空目录）
└── services/            # 业务逻辑（空目录）
```

## 已完成的部分

- `app/core/config.py` — 配置类，DATABASE_URL 格式已留空需填写
- `app/core/security.py` — 四个函数：verify_password、get_password_hash、create_access_token、verify_token，均有 Docstring
- `app/datebase.py` — 数据库连接（注意：文件名有拼写错误，应该是 database.py）

## 当前开发进度

下一步：**创建所有 SQLAlchemy 模型（models 层）**

参考设计文档 `docs/superpowers/specs/2026-05-05-delta陪玩店票务系统-design.md`，需要创建的模型文件：

- `app/models/shop.py` — ShopOwner 店家
- `app/models/booster.py` — Booster 打手 + BoosterPrice 报价
- `app/models/customer.py` — Customer 客户
- `app/models/order.py` — Order 订单
- `app/models/review.py` — Review 评价
- `app/models/reservation.py` — Reservation 预约

## 待完成的部分

models 全部完成后，继续：
1. schemas（Pydantic 格式校验）
2. dependencies.py（三个角色的认证依赖）
3. main.py（入口 + 路由注册）
4. 四个业务模块的 service + router

## 技术要点

- 数据库：MySQL（需安装 pymysql），已安装依赖：fastapi, uvicorn, sqlalchemy, pydantic, pydantic_settings, python jose, passlib, bcrypt, pymysql
- 密码哈希：bcrypt，通过 passlib 的 CryptContext 使用
- Token：JWT，HS256 算法，7 天有效期，sub 字段存用户名
- 平台抽成：20%（PLATFORM_COMMISSION = 0.20）
- 支付：当前版本预留，不接入真实支付

## 设计文档位置

`docs/superpowers/specs/2026-05-05-delta陪玩店票务系统-design.md` — 包含完整的数据表设计、API 路由设计、订单状态流转
`docs/folder-structure.md` — 文件夹结构说明
`docs/fastapi-tutor.md` — 引导式学习教程（当用户想自学时使用）

## 文件名拼写错误

注意：`app/datebase.py` 应为 `app/database.py`，后续创建文件时使用正确拼写。
