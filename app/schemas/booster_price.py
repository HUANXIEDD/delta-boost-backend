from pydantic import BaseModel


class BoosterPriceBase(BaseModel):
    """报价基础字段"""
    service_type: str
    price: int  # 单位：分


class BoosterPriceCreate(BoosterPriceBase):
    """打手设置报价时接收的数据"""
    pass


class BoosterPriceUpdate(BaseModel):
    """打手更新报价时接收的数据（支持只改价格或只改服务类型）"""
    service_type: str | None = None
    price: int | None = None


class BoosterPriceResponse(BoosterPriceBase):
    """API 返回的报价信息"""
    id: int
    booster_id: int

    model_config = {"from_attributes": True}
