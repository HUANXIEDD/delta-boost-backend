from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BoosterBase(BaseModel):
    """打手基础字段，所有schemas共享"""
    unique_id: str
    username: str


class BoosterCreate(BoosterBase):
    """打手注册时接收的数据"""
    password: str  # 明文密码，会自动哈希


class BoosterLogin(BaseModel):
    """打手登录时接收的数据"""
    username: str
    password: str


class BoosterUpdate(BaseModel):
    """打手更新个人信息时接收的数据"""
    avatar: str | None = None
    bio: str | None = None
    services: list[str] | None = None  # 擅长服务列表，如 ["护航", "情绪"]


class BoosterResponse(BoosterBase):
    """API 返回给客户端的打手信息"""
    id: int
    avatar: str | None = None
    bio: str | None = None
    services: str | None = None  # 数据库存的是JSON字符串
    is_busy: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
