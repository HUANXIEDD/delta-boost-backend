from datetime import datetime

from pydantic import BaseModel


class CustomerBase(BaseModel):
    """客户基础字段"""
    username: str


class CustomerCreate(CustomerBase):
    """客户注册时接收的数据"""
    password: str


class CustomerLogin(BaseModel):
    """客户登录时接收的数据"""
    username: str
    password: str


class CustomerResponse(CustomerBase):
    """API 返回给客户端的客户信息"""
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
