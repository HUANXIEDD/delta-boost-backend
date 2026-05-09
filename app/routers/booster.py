import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_booster
from app.models import Booster, BoosterPrice, Order, Review
from app.schemas import ReviewReply
from app.schemas.booster import (
    BoosterCreate, BoosterLogin, BoosterUpdate, BoosterResponse, BoosterSwitchStatus
)
from app.schemas.booster_price import BoosterPriceCreate, BoosterPriceResponse, BoosterPriceUpdate
from app.core.security import verify_password, get_password_hash, create_access_token


def generate_booster_unique_id(db: Session) -> str:
    latest = db.query(Booster).order_by(Booster.id.desc()).first()
    if latest:
        num = int(latest.unique_id[3:]) + 1
    else:
        num = 1
    return f"BST{num:03d}"


router = APIRouter(prefix="/booster", tags=["打手"])


# ==================== 注册 & 登录 ====================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_booster(data: BoosterCreate, db: Session = Depends(get_db)):
    existing = db.query(Booster).filter(Booster.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="此打手已存在")
    hashed = get_password_hash(data.password)
    booster = Booster(
        username=data.username,
        password_hash=hashed,
        unique_id=generate_booster_unique_id(db)
    )
    db.add(booster)
    db.commit()
    db.refresh(booster)
    return {"message": "注册成功", "booster_id": booster.id}


@router.post("/login")
def login_booster(data: BoosterLogin, db: Session = Depends(get_db)):
    booster = db.query(Booster).filter(Booster.username == data.username).first()
    if not booster:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(data.password, booster.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": booster.username, "role": "booster"})
    return {"access_token": token, "token_type": "bearer"}


# ==================== 个人信息 ====================

@router.get("/profile")
def get_profile(current_booster: Booster = Depends(get_current_booster)):
    return current_booster


@router.post("/profile")
def update_profile(
    data: BoosterUpdate,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    if data.avatar is not None:
        current_booster.avatar = data.avatar
    if data.bio is not None:
        current_booster.bio = data.bio
    if data.services is not None:
        current_booster.services = json.dumps(data.services)
    db.commit()
    db.refresh(current_booster)
    return {"message": "更新成功", "booster": current_booster}


# ==================== 报价 ====================

@router.get("/prices")
def get_prices(current_booster: Booster = Depends(get_current_booster)):
    return current_booster.prices


@router.post("/prices")
def set_prices(
    data: list[BoosterPriceCreate],
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    # 删除旧报价，插入新报价
    db.query(BoosterPrice).filter(
        BoosterPrice.booster_id == current_booster.id
    ).delete()
    for p in data:
        bp = BoosterPrice(
            booster_id=current_booster.id,
            service_type=p.service_type,
            price=p.price,
        )
        db.add(bp)
    db.commit()
    return {"message": "报价已更新"}


# ==================== 状态 ====================

@router.post("/status")
def switch_status(
    data: BoosterSwitchStatus,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    current_booster.is_busy = data.is_busy
    db.commit()
    return {"message": "状态更新成功", "is_busy": current_booster.is_busy}


# ==================== 订单 ====================

@router.get("/orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    orders = db.query(Order).filter(
        Order.booster_id == current_booster.id
    ).all()
    return orders


@router.post("/orders/{order_id}/accept")
def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    if order.status != "created":
        raise HTTPException(status_code=400, detail="订单状态不允许接单")

    order.status = "accepted"
    current_booster.is_busy = True
    db.commit()
    return {"message": "接单成功"}


@router.post("/orders/{order_id}/reject")
def reject_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    if order.status != "created":
        raise HTTPException(status_code=400, detail="订单状态不允许拒单")

    order.status = "cancelled"
    db.commit()
    return {"message": "已拒绝订单"}


@router.post("/orders/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    if order.status != "accepted":
        raise HTTPException(status_code=400, detail="订单状态不允许完成")

    order.status = "completed"
    order.completed_at = datetime.utcnow()
    current_booster.is_busy = False
    db.commit()
    return {"message": "服务已完成"}


# ==================== 评价 ====================

@router.get("/reviews")
def get_my_reviews(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    reviews = db.query(Review).filter(
        Review.booster_id == current_booster.id
    ).all()
    return reviews


@router.post("/reviews/{review_id}/reply")
def reply_review(
    review_id: int,
    data: ReviewReply,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    if review.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的评价，不能回复")

    review.reply = data.reply
    db.commit()
    return {"message": "回复成功"}
