from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Order(Base):
    """订单模型"""

    __tablename__ = "orders"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 订单号（唯一）
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    # 外键：关联客户
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)

    # 外键：关联打手（指定打手时）
    booster_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("boosters.id"), nullable=True)

    # 选中的服务类型列表，存JSON
    services: Mapped[str] = mapped_column(String(255), nullable=False)

    # 客户自定义需求描述
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 客户预算（存整数，单位：分）
    budget: Mapped[int] = mapped_column(Integer, nullable=False)

    # 状态：created/accepted/completed/confirmed/cancelled/expired
    status: Mapped[str] = mapped_column(String(20), default="created")

    # 是否为预约单
    is_reservation: Mapped[bool] = mapped_column(Boolean, default=False)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 客户确认完成时间
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 打手完成时间
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 关系
    customer = relationship("Customer", back_populates="orders")
    booster = relationship("Booster", back_populates="orders")
    review = relationship("Review", back_populates="order", uselist=False)
