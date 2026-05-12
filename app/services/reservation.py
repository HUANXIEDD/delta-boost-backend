import json
from sqlalchemy.orm import Session

from app.models import Booster, Customer, Reservation


def create_reservation(
    db: Session,
    customer_id: int,
    booster_id: int,
    services: list[str],
    budget: int,
) -> Reservation:
    """客户创建预约"""
    reservation = Reservation(
        customer_id=customer_id,
        booster_id=booster_id,
        services=json.dumps(services),
        budget=budget,
        status="pending",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_reservations_by_customer(db: Session, customer_id: int) -> list[Reservation]:
    """获取客户的所有预约"""
    return db.query(Reservation).filter(Reservation.customer_id == customer_id).all()


def get_reservations_by_booster(db: Session, booster_id: int) -> list[Reservation]:
    """获取打手的所有预约"""
    return db.query(Reservation).filter(Reservation.booster_id == booster_id).order_by(
        Reservation.created_at.desc()
    ).all()


def get_all_reservations(db: Session, status_filter: str | None = None) -> list[Reservation]:
    """获取所有预约（店家视角）"""
    query = db.query(Reservation)
    if status_filter:
        query = query.filter(Reservation.status == status_filter)
    return query.order_by(Reservation.created_at.desc()).all()


def accept_reservation(db: Session, reservation: Reservation) -> Reservation:
    """打手接受预约：pending → accepted"""
    if reservation.status != "pending":
        raise ValueError(f"预约状态已是 {reservation.status}，无法接受")
    reservation.status = "accepted"
    db.commit()
    db.refresh(reservation)
    return reservation


def reject_reservation(db: Session, reservation: Reservation) -> Reservation:
    """打手拒绝预约：pending → rejected"""
    if reservation.status != "pending":
        raise ValueError(f"预约状态已是 {reservation.status}，无法拒绝")
    reservation.status = "rejected"
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    """打手取消已接受的预约：accepted → cancelled"""
    if reservation.status != "accepted":
        raise ValueError(f"预约状态已是 {reservation.status}，无法取消")
    reservation.status = "cancelled"
    db.commit()
    db.refresh(reservation)
    return reservation