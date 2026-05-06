from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.database import get_db
from app.models import Booster, Customer, ShopOwner

# Bearer Token 认证 scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    验证 Token，返回 {"sub": 用户名, "role": 角色}

    所有角色共用的认证依赖
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )

    return payload


def get_current_shop(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ShopOwner:
    """
    店家专用认证依赖
    验证 Token 属于店家，返回 ShopOwner 对象
    """
    if payload.get("role") != "shop":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要店家身份",
        )

    username = payload.get("sub")
    shop = db.query(ShopOwner).filter(ShopOwner.username == username).first()
    if shop is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="店家不存在",
        )

    return shop


def get_current_booster(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Booster:
    """
    打手专用认证依赖
    验证 Token 属于打手，返回 Booster 对象
    """
    if payload.get("role") != "booster":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要打手身份",
        )

    username = payload.get("sub")
    booster = db.query(Booster).filter(Booster.username == username).first()
    if booster is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="打手不存在",
        )

    return booster


def get_current_customer(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Customer:
    """
    客户专用认证依赖
    验证 Token 属于客户，返回 Customer 对象
    """
    if payload.get("role") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要客户身份",
        )

    username = payload.get("sub")
    customer = db.query(Customer).filter(Customer.username == username).first()
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="客户不存在",
        )

    return customer
