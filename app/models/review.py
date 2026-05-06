from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    """评价模型"""

    __tablename__ = "reviews"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 外键：关联订单
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)

    # 外键：关联客户
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)

    # 外键：关联打手
    booster_id: Mapped[int] = mapped_column(Integer, ForeignKey("boosters.id"), nullable=False)

    # 服务态度 1-5
    attitude_star: Mapped[int] = mapped_column(Integer, nullable=False)

    # 情绪价值 1-5
    emotion_star: Mapped[int] = mapped_column(Integer, nullable=False)

    # 局内表现 1-5
    performance_star: Mapped[int] = mapped_column(Integer, nullable=False)

    # 评价内容
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 打手回复
    reply: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 评价时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    order = relationship("Order", back_populates="review")
    customer = relationship("Customer", back_populates="reviews")
    booster = relationship("Booster", back_populates="reviews")