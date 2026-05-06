from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """客户提交评价时接收的数据"""
    order_id: int
    attitude_star: int = Field(ge=1, le=5)   # 1-5 分
    emotion_star: int = Field(ge=1, le=5)    # 1-5 分
    performance_star: int = Field(ge=1, le=5) # 1-5 分
    content: str | None = None


class ReviewReply(BaseModel):
    """打手回复评价时接收的数据"""
    reply: str


class ReviewResponse(BaseModel):
    """API 返回的评价信息"""
    id: int
    order_id: int
    customer_id: int
    booster_id: int
    attitude_star: int
    emotion_star: int
    performance_star: int
    content: str | None
    reply: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
