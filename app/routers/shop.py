from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_shop
from app.models import Booster, Order, Reservation, Review, ShopOwner
from app.schemas import ShopLogin, ShopResponse
import app.services.shop as shop_service
import app.services.booster as booster_service
import app.services.order as order_service
import app.services.reservation as reservation_service
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/shop", tags=["店家"])


@router.post("/login")
def login(data: ShopLogin, db: Session = Depends(get_db)):
    """店家登录"""
    shop = shop_service.get_shop_by_username(db, data.username)
    if not shop:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(data.password, shop.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": shop.username, "role": "shop"})
    return {"message": "登录成功", "access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=ShopResponse)
def get_profile(current_shop: ShopOwner = Depends(get_current_shop)):
    """获取店家信息"""
    return current_shop


# ==================== 打手管理 ====================

@router.get("/boosters")
def list_boosters(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """查看打手列表"""
    boosters = booster_service.get_all_boosters(db, status_filter)
    return [
        {
            "id": b.id,
            "unique_id": b.unique_id,
            "username": b.username,
            "avatar": b.avatar,
            "bio": b.bio,
            "services": b.services,
            "is_busy": b.is_busy,
            "status": b.status,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in boosters
    ]


@router.post("/boosters/{booster_id}/approve")
def approve_booster(
    booster_id: int,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """审核通过打手"""
    booster = booster_service.get_booster_by_id(db, booster_id)
    if not booster:
        raise HTTPException(status_code=404, detail="打手不存在")
    if booster.status != "pending":
        raise HTTPException(status_code=400, detail=f"打手状态已是 {booster.status}，无法审批")
    booster_service.update_booster_status(db, booster, "approved")
    return {"message": "已通过打手审核"}


@router.post("/boosters/{booster_id}/reject")
def reject_booster(
    booster_id: int,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """审核拒绝打手"""
    booster = booster_service.get_booster_by_id(db, booster_id)
    if not booster:
        raise HTTPException(status_code=404, detail="打手不存在")
    if booster.status != "pending":
        raise HTTPException(status_code=400, detail=f"打手状态已是 {booster.status}，无法审批")
    booster_service.update_booster_status(db, booster, "rejected")
    return {"message": "已拒绝打手"}


@router.post("/boosters/{booster_id}/disable")
def disable_booster(
    booster_id: int,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """禁用打手"""
    booster = booster_service.get_booster_by_id(db, booster_id)
    if not booster:
        raise HTTPException(status_code=404, detail="打手不存在")
    booster_service.update_booster_status(db, booster, "disabled")
    return {"message": "已禁用打手"}


# ==================== 订单查看 ====================

@router.get("/orders")
def list_all_orders(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """店家查看所有订单"""
    orders = order_service.get_all_orders(db, status_filter)
    return [
        {
            "id": o.id,
            "order_no": o.order_no,
            "customer_id": o.customer_id,
            "booster_id": o.booster_id,
            "services": o.services,
            "requirements": o.requirements,
            "budget": o.budget,
            "status": o.status,
            "is_reservation": o.is_reservation,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "confirmed_at": o.confirmed_at.isoformat() if o.confirmed_at else None,
            "completed_at": o.completed_at.isoformat() if o.completed_at else None,
        }
        for o in orders
    ]


@router.get("/orders/{order_id}")
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """查看订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order_service.get_order_detail(db, order)


# ==================== 预约查看 ====================

@router.get("/reservations")
def list_reservations(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """店家查看所有预约"""
    reservations = reservation_service.get_all_reservations(db, status_filter)
    return [
        {
            "id": r.id,
            "customer_id": r.customer_id,
            "booster_id": r.booster_id,
            "services": r.services,
            "budget": r.budget,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reservations
    ]


# ==================== 统计 ====================

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_shop: ShopOwner = Depends(get_current_shop),
):
    """获取平台统计数据"""
    return order_service.get_platform_stats(db)