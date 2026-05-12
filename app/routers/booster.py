from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_booster
from app.models import Booster, Order, Review
from app.schemas import BoosterLogin, BoosterResponse
from app.schemas.booster import BoosterCreate, BoosterUpdate, BoosterSwitchStatus
from app.schemas.booster_price import BoosterPriceCreate
from app.schemas.review import ReviewReply
import app.services.booster as booster_service
import app.services.order as order_service
import app.services.review as review_service
import app.services.reservation as reservation_service
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/booster", tags=["打手"])


# ==================== 注册 & 登录 ====================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_booster(data: BoosterCreate, db: Session = Depends(get_db)):
    """打手注册"""
    existing = booster_service.get_booster_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="此打手已存在")
    booster = booster_service.create_booster(db, data)
    return {"message": "注册成功", "booster_id": booster.id}


@router.post("/login")
def login_booster(data: BoosterLogin, db: Session = Depends(get_db)):
    """打手登录"""
    booster = booster_service.get_booster_by_username(db, data.username)
    if not booster:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(data.password, booster.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": booster.username, "role": "booster"})
    return {"access_token": token, "token_type": "bearer"}


# ==================== 个人信息 ====================

@router.get("/profile")
def get_profile(current_booster: Booster = Depends(get_current_booster)):
    """获取个人信息"""
    return current_booster


@router.post("/profile")
def update_profile(
    data: BoosterUpdate,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """更新个人信息"""
    import json
    services = json.dumps(data.services) if data.services is not None else None
    booster_service.update_booster_profile(
        db, current_booster,
        avatar=data.avatar, bio=data.bio, services=services
    )
    return {"message": "更新成功"}


# ==================== 报价 ====================

@router.get("/prices")
def get_prices(current_booster: Booster = Depends(get_current_booster)):
    """获取我的报价"""
    return current_booster.prices


@router.post("/prices")
def set_prices(
    data: list[BoosterPriceCreate],
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """设置报价"""
    booster_service.set_booster_prices(db, current_booster, data)
    return {"message": "报价已更新"}


# ==================== 状态 ====================

@router.post("/status")
def switch_status(
    data: BoosterSwitchStatus,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """切换忙碌状态"""
    booster_service.switch_booster_status(db, current_booster, data.is_busy)
    return {"message": "状态更新成功", "is_busy": current_booster.is_busy}


# ==================== 订单 ====================

@router.get("/orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """查看我的订单"""
    return order_service.get_orders_by_booster(db, current_booster.id)


@router.post("/orders/{order_id}/accept")
def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """接单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    try:
        order_service.accept_order(db, order, current_booster)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "接单成功"}


@router.post("/orders/{order_id}/reject")
def reject_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """拒单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    try:
        order_service.reject_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "已拒绝订单"}


@router.post("/orders/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """完成服务"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的订单")
    try:
        order_service.complete_order(db, order, current_booster)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "服务已完成"}


# ==================== 评价 ====================

@router.get("/reviews")
def get_my_reviews(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """查看我的评价"""
    return review_service.get_reviews_by_booster(db, current_booster.id)


@router.post("/reviews/{review_id}/reply")
def reply_review(
    review_id: int,
    data: ReviewReply,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """回复评价"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    if review.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的评价，不能回复")
    review_service.reply_review(db, review, data.reply)
    return {"message": "回复成功"}


# ==================== 预约 ====================

@router.get("/reservations")
def get_my_reservations(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """查看我的预约"""
    return reservation_service.get_reservations_by_booster(db, current_booster.id)