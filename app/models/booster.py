from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Booster(Base):
    __tablename__ = "boosters"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 用户可见的唯一标识，如 "BST001"
    unique_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # 用户名
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 密码哈希
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # 头像URL
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 简介
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 擅长服务列表，存JSON格式
    services: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 是否忙碌
    is_busy: Mapped[bool] = mapped_column(Boolean, default=False)

    # 状态：pending/approved/rejected/disabled
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系：一个打手可以有多个报价
    prices = relationship("BoosterPrice", back_populates="booster")
    orders = relationship("Order", back_populates="booster")
    reviews = relationship("Review", back_populates="booster")
    reservations = relationship("Reservation", back_populates="booster")


class BoosterPrice(Base):
    __tablename__ = "booster_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 外键：关联到 Booster 表
    booster_id: Mapped[int] = mapped_column(Integer, ForeignKey("boosters.id"), nullable=False)

    # 服务类型：护航/情绪/男陪/女陪
    service_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # 单价（存整数，单位：分）
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # 反向关联：属于哪个打手
    booster = relationship("Booster", back_populates="prices")
