from sqlalchemy.orm import Session

from app.models import Customer
from app.core.security import get_password_hash, verify_password, create_access_token


def create_customer(db: Session, username: str, password: str) -> Customer:
    """注册客户"""
    customer = Customer(
        username=username,
        password_hash=get_password_hash(password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_by_username(db: Session, username: str):
    """根据用户名查询客户"""
    return db.query(Customer).filter(Customer.username == username).first()


def authenticate_customer(db: Session, username: str, password: str):
    """验证客户登录，返回 token 或 None"""
    customer = get_customer_by_username(db, username)
    if not customer:
        return None
    if not verify_password(password, customer.password_hash):
        return None
    token = create_access_token({"sub": customer.username, "role": "customer"})
    return token