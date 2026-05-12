import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Booster, BoosterPrice, Customer, Order


def generate_order_no() -> str:
    """生成唯一订单号：前缀 + 时间戳 + 随机字符"""
    from datetime import datetime
    import uuid
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand = uuid.uuid4().hex[:4].upper()
    return f"ORD{ts}{rand}"


def expire_pending_orders(db: Session):
    """查询时顺便把超过30分钟未支付的订单取消"""
    cutoff = datetime.utcnow().timestamp() - 30 * 60
    expired = db.query(Order).filter(
        Order.status == "pending_payment",
        Order.created_at.timestamp() < cutoff,
    ).all()
    for o in expired:
        o.status = "cancelled"
    if expired:
        db.commit()
    return len(expired)


def search_boosters(
    db: Session,
    services: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    is_busy: bool | None = None,
):
    """
    搜索打手，支持服务、价格、忙碌状态筛选。
    services 支持逗号分隔的多选（AND 逻辑：打手必须同时拥有所有服务）
    """
    query = db.query(Booster).filter(Booster.status == "approved")
    if is_busy is not None:
        query = query.filter(Booster.is_busy == is_busy)
    boosters = query.all()

    service_list = [s.strip() for s in services.split(",")] if services else []

    if service_list or min_price or max_price:
        filtered = []
        for b in boosters:
            prices = db.query(BoosterPrice).filter(BoosterPrice.booster_id == b.id).all()
            booster_service_types = [p.service_type for p in prices]

            if service_list and not all(s in booster_service_types for s in service_list):
                continue

            if min_price or max_price:
                price_vals = [p.price for p in prices]
                if min_price and min(price_vals, default=0) < min_price:
                    continue
                if max_price and max(price_vals, default=999999999) > max_price:
                    continue
            filtered.append(b)
        boosters = filtered

    result = []
    for b in boosters:
        prices = db.query(BoosterPrice).filter(BoosterPrice.booster_id == b.id).all()
        result.append({
            "id": b.id,
            "unique_id": b.unique_id,
            "username": b.username,
            "avatar": b.avatar,
            "bio": b.bio,
            "services": json.loads(b.services) if b.services else [],
            "is_busy": b.is_busy,
            "prices": [{"service_type": p.service_type, "price": p.price} for p in prices],
        })
    return result


def create_order(
    db: Session,
    customer_id: int,
    booster_id: int | None,
    services: list[str],
    requirements: str | None,
    budget: int,
    is_reservation: bool = False,
) -> Order:
    """创建订单，初始状态为 pending_payment"""
    order = Order(
        order_no=generate_order_no(),
        customer_id=customer_id,
        booster_id=booster_id,
        services=json.dumps(services),
        requirements=requirements,
        budget=budget,
        is_reservation=is_reservation,
        status="pending_payment",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def pay_order(db: Session, order: Order) -> Order:
    """模拟支付：pending_payment → created"""
    expire_pending_orders(db)
    if order.status == "cancelled":
        raise ValueError("订单已超时取消，请重新下单")
    if order.status != "pending_payment":
        raise ValueError(f"当前状态是 {order.status}，无法支付")
    order.status = "created"
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order: Order) -> Order:
    """取消订单（仅限 pending_payment / created 状态）"""
    expire_pending_orders(db)
    if order.status not in ("pending_payment", "created"):
        raise ValueError(f"当前状态是 {order.status}，无法取消")
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order


def confirm_order(db: Session, order: Order) -> Order:
    """客户确认服务完成：completed → confirmed"""
    if order.status != "completed":
        raise ValueError("打手尚未完成服务，当前状态：" + order.status)
    order.status = "confirmed"
    order.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


def accept_order(db: Session, order: Order, booster: Booster) -> Order:
    """打手接单：created → accepted，同时设置打手为忙碌"""
    expire_pending_orders(db)
    if order.status != "created":
        raise ValueError("订单状态不允许接单")
    order.status = "accepted"
    booster.is_busy = True
    db.commit()
    db.refresh(order)
    return order


def reject_order(db: Session, order: Order) -> Order:
    """打手拒单：created → cancelled"""
    expire_pending_orders(db)
    if order.status != "created":
        raise ValueError("订单状态不允许拒单")
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order


def complete_order(db: Session, order: Order, booster: Booster) -> Order:
    """打手完成服务：accepted → completed"""
    if order.status != "accepted":
        raise ValueError("订单状态不允许完成")
    order.status = "completed"
    order.completed_at = datetime.utcnow()
    booster.is_busy = False
    db.commit()
    db.refresh(order)
    return order


def get_orders_by_customer(db: Session, customer_id: int) -> list[Order]:
    """获取客户的所有订单"""
    expire_pending_orders(db)
    return db.query(Order).filter(Order.customer_id == customer_id).all()


def get_orders_by_booster(db: Session, booster_id: int) -> list[Order]:
    """获取打手的所有订单"""
    expire_pending_orders(db)
    return db.query(Order).filter(Order.booster_id == booster_id).all()


def get_all_orders(db: Session, status_filter: str | None = None) -> list[Order]:
    """获取所有订单（店家视角）"""
    expire_pending_orders(db)
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    return query.order_by(Order.created_at.desc()).all()


def get_order_detail(db: Session, order: Order):
    """获取订单详情（含客户名、打手名、评价）"""
    from app.models import Customer, Review

    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    booster = db.query(Booster).filter(Booster.id == order.booster_id).first() if order.booster_id else None
    review = db.query(Review).filter(Review.order_id == order.id).first()

    return {
        "id": order.id,
        "order_no": order.order_no,
        "customer_id": order.customer_id,
        "customer_username": customer.username if customer else None,
        "booster_id": order.booster_id,
        "booster_username": booster.username if booster else None,
        "services": json.loads(order.services) if order.services else [],
        "requirements": order.requirements,
        "budget": order.budget,
        "status": order.status,
        "is_reservation": order.is_reservation,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "review": {
            "attitude_star": review.attitude_star,
            "emotion_star": review.emotion_star,
            "performance_star": review.performance_star,
            "content": review.content,
            "reply": review.reply,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        } if review else None,
    }


def get_platform_stats(db: Session):
    """获取平台统计数据"""
    expire_pending_orders(db)
    from app.models import Booster, Order

    total_boosters = db.query(Booster).count()
    approved_boosters = db.query(Booster).filter(Booster.status == "approved").count()
    pending_boosters = db.query(Booster).filter(Booster.status == "pending").count()

    total_orders = db.query(Order).count()
    total_revenue = sum(o.budget for o in db.query(Order).filter(Order.status == "confirmed").all())
    platform_commission = int(total_revenue * 0.20)

    return {
        "total_boosters": total_boosters,
        "approved_boosters": approved_boosters,
        "pending_boosters": pending_boosters,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "platform_commission": platform_commission,
        "net_revenue": total_revenue - platform_commission,
    }