from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    """客户模型"""

    __tablename__ = "customers"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 用户名
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 密码哈希
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    reservations = relationship("Reservation", back_populates="customer")
