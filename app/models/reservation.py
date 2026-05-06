from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reservation(Base):
    """预约模型"""

    __tablename__ = "reservations"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 外键：关联客户
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)

    # 外键：关联打手
    booster_id: Mapped[int] = mapped_column(Integer, ForeignKey("boosters.id"), nullable=False)

    # 预约的服务类型，存JSON
    services: Mapped[str] = mapped_column(String(255), nullable=False)

    # 预约预算（存整数，单位：分）
    budget: Mapped[int] = mapped_column(Integer, nullable=False)

    # 状态：pending/accepted/rejected/cancelled
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # 预约时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    customer = relationship("Customer", back_populates="reservations")
    booster = relationship("Booster", back_populates="reservations")
