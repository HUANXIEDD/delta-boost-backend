from datetime import datetime

from pydantic import BaseModel


class ReservationCreate(BaseModel):
    """客户创建预约时接收的数据"""
    booster_id: int
    services: list[str]  # 预约的服务类型
    budget: int          # 预算（单位：分）


class ReservationStatusUpdate(BaseModel):
    """打手更新预约状态时接收的数据"""
    status: str  # accepted / rejected


class ReservationResponse(BaseModel):
    """API 返回的预约信息"""
    id: int
    customer_id: int
    booster_id: int
    services: str          # JSON 字符串
    budget: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
