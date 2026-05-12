from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_customer
from app.models import Customer, Order
import app.models
from app.schemas import CustomerCreate, CustomerLogin, CustomerResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.reservation import ReservationCreate
from app.schemas.review import ReviewCreate
import app.services.order as order_service
import app.services.customer as customer_service
import app.services.reservation as reservation_service
import app.services.review as review_service


router = APIRouter(prefix="/customer", tags=["客户"])


# ==================== 注册 & 登录 ====================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    """客户注册"""
    existing = customer_service.get_customer_by_username(db, data.username)
    if existing:
        raise HTTPException(status_code=400, detail="此用户名已存在")
    customer_service.create_customer(db, data.username, data.password)
    return {"message": "注册成功"}


@router.post("/login")
def login_customer(data: CustomerLogin, db: Session = Depends(get_db)):
    """客户登录"""
    token = customer_service.authenticate_customer(db, data.username, data.password)
    if not token:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"access_token": token, "token_type": "bearer"}


# ==================== 个人信息 ====================

@router.get("/profile", response_model=CustomerResponse)
def get_profile(current_customer: Customer = Depends(get_current_customer)):
    """获取当前客户信息"""
    return current_customer


# ==================== 搜索打手 ====================

@router.get("/boosters")
def search_boosters(
    services: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    is_busy: bool | None = None,
    db: Session = Depends(get_db),
):
    """搜索打手列表"""
    return order_service.search_boosters(db, services, min_price, max_price, is_busy)


# ==================== 预约 ====================

@router.post("/reservations", status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """客户创建预约请求"""
    booster = order_service.search_boosters(db, is_busy=False)
    booster_ids = [b["id"] for b in booster]
    if data.booster_id not in booster_ids:
        raise HTTPException(status_code=400, detail="打手不存在或未通过审核")

    reservation_service.create_reservation(
        db, current_customer.id, data.booster_id, data.services, data.budget
    )
    return {"message": "预约已提交"}


@router.get("/reservations")
def get_my_reservations(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """查看我的预约"""
    return reservation_service.get_reservations_by_customer(db, current_customer.id)


# ==================== 订单 ====================

@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """客户创建订单（待支付状态）"""
    booster = None
    if data.booster_id:
        booster = db.query(app.models.Booster).filter(
            app.models.Booster.id == data.booster_id
        ).first()
        if not booster:
            raise HTTPException(status_code=404, detail="指定的打手不存在")
        if booster.status != "approved":
            raise HTTPException(status_code=400, detail="打手未通过审核，无法接单")
        if booster.is_busy:
            raise HTTPException(status_code=400, detail="打手正在忙碌中")

    order = order_service.create_order(
        db,
        customer_id=current_customer.id,
        booster_id=data.booster_id,
        services=data.services,
        requirements=data.requirements,
        budget=data.budget,
        is_reservation=data.is_reservation,
    )
    return {"message": "订单已创建，请在30分钟内支付", "order_id": order.id, "order_no": order.order_no}


@router.post("/orders/{order_id}/pay")
def pay_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """模拟支付：pending_payment → created"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    try:
        order_service.pay_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "支付成功，等待打手接单"}


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """客户取消订单（仅限待支付和已创建状态）"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    try:
        order_service.cancel_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "订单已取消"}


@router.get("/orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """查看我的订单列表"""
    return order_service.get_orders_by_customer(db, current_customer.id)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """查看指定订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="无权查看此订单")
    return order


@router.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """客户确认服务完成"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    try:
        order_service.confirm_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "已确认服务完成"}


# ==================== 评价 ====================

@router.post("/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """客户提交评价"""
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="无权评价此订单")
    if order.status != "confirmed":
        raise HTTPException(status_code=400, detail="只能在确认完成后评价")

    existing = db.query(app.models.Review).filter(
        app.models.Review.order_id == data.order_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该订单已评价")

    review_service.create_review(
        db,
        order_id=data.order_id,
        customer_id=current_customer.id,
        booster_id=order.booster_id,
        attitude_star=data.attitude_star,
        emotion_star=data.emotion_star,
        performance_star=data.performance_star,
        content=data.content,
    )
    return {"message": "评价已提交"}


@router.get("/reviews")
def get_my_reviews(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """查看我的评价记录"""
    return review_service.get_reviews_by_customer(db, current_customer.id)