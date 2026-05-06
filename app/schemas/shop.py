from pydantic import BaseModel


class ShopLogin(BaseModel):
    """店家登录时接收的数据"""
    username: str
    password: str


class ShopResponse(BaseModel):
    """API 返回给客户端的店家信息"""
    id: int
    username: str

    model_config = {"from_attributes": True}
