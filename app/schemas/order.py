from datetime import datetime

from pydantic import BaseModel


class OrderCreate(BaseModel):
    """客户创建订单时接收的数据"""
    booster_id: int | None = None  # 可选，指定打手
    services: list[str]            # 服务类型列表，如 ["护航", "情绪"]
    requirements: str | None = None  # 自定义需求
    budget: int                     # 预算（单位：分）
    is_reservation: bool = False    # 是否为预约单


class OrderStatusUpdate(BaseModel):
    """打手更新订单状态时接收的数据（接受/拒绝/完成）"""
    status: str  # accepted / rejected / completed


class OrderConfirm(BaseModel):
    """客户确认服务完成时接收的数据"""
    pass  # 不需要额外参数，状态自动变为 confirmed


class OrderResponse(BaseModel):
    """API 返回的订单信息"""
    id: int
    order_no: str
    customer_id: int
    booster_id: int | None
    services: str              # JSON 字符串
    requirements: str | None
    budget: int
    status: str
    is_reservation: bool
    created_at: datetime
    confirmed_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}
