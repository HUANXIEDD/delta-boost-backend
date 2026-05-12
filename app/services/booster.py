from sqlalchemy.orm import Session

from app.models import Booster, BoosterPrice
from app.schemas.booster import BoosterCreate
from app.core.security import get_password_hash


def generate_booster_unique_id(db: Session) -> str:
    """生成打手唯一ID：BST001, BST002, ..."""
    latest = db.query(Booster).order_by(Booster.id.desc()).first()
    if latest:
        num = int(latest.unique_id[3:]) + 1
    else:
        num = 1
    return f"BST{num:03d}"


def create_booster(db: Session, data: BoosterCreate) -> Booster:
    """注册打手"""
    booster = Booster(
        username=data.username,
        password_hash=get_password_hash(data.password),
        unique_id=generate_booster_unique_id(db),
    )
    db.add(booster)
    db.commit()
    db.refresh(booster)
    return booster


def get_booster_by_username(db: Session, username: str):
    """根据用户名查询打手"""
    return db.query(Booster).filter(Booster.username == username).first()


def get_booster_by_id(db: Session, booster_id: int):
    """根据ID查询打手"""
    return db.query(Booster).filter(Booster.id == booster_id).first()


def update_booster_profile(
    db: Session, booster: Booster, avatar=None, bio=None, services=None
):
    """更新打手个人信息"""
    if avatar is not None:
        booster.avatar = avatar
    if bio is not None:
        booster.bio = bio
    if services is not None:
        booster.services = services
    db.commit()
    db.refresh(booster)
    return booster


def set_booster_prices(db: Session, booster: Booster, prices_data: list):
    """设置打手报价（先删后插）"""
    db.query(BoosterPrice).filter(BoosterPrice.booster_id == booster.id).delete()
    for p in prices_data:
        bp = BoosterPrice(
            booster_id=booster.id,
            service_type=p.service_type,
            price=p.price,
        )
        db.add(bp)
    db.commit()


def switch_booster_status(db: Session, booster: Booster, is_busy: bool):
    """切换打手忙碌状态"""
    booster.is_busy = is_busy
    db.commit()
    return booster


def get_approved_boosters(db: Session):
    """获取所有已审核通过的打手"""
    return db.query(Booster).filter(Booster.status == "approved").all()


def get_all_boosters(db: Session, status_filter: str | None = None):
    """获取打手列表（店家视角）"""
    query = db.query(Booster)
    if status_filter:
        query = query.filter(Booster.status == status_filter)
    return query.all()


def update_booster_status(db: Session, booster: Booster, status: str):
    """更新打手审核状态：approved / rejected / disabled"""
    booster.status = status
    db.commit()
    return booster