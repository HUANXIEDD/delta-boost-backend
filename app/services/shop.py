from sqlalchemy.orm import Session

from app.models import ShopOwner
from app.core.security import verify_password, create_access_token


def get_shop_by_username(db: Session, username: str):
    """根据用户名查询店家"""
    return db.query(ShopOwner).filter(ShopOwner.username == username).first()


def authenticate_shop(db: Session, username: str, password: str):
    """验证店家登录，返回 token 或 None"""
    shop = get_shop_by_username(db, username)
    if not shop:
        return None
    if not verify_password(password, shop.password_hash):
        return None
    token = create_access_token({"sub": shop.username, "role": "shop"})
    return token