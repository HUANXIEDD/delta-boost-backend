from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShopOwner(Base):
    """店家模型"""

    __tablename__ = "shop_owners"

    # 主键，自增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 用户名
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 密码哈希
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)