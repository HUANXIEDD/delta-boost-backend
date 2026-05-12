from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_booster
from app.models import Booster, Reservation
import app.services.reservation as reservation_service


router = APIRouter(prefix="/reservation", tags=["预约"])


# ==================== 预约查看 ====================

@router.get("/")
def get_my_reservations(
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """打手查看自己的预约列表"""
    return reservation_service.get_reservations_by_booster(db, current_booster.id)


# ==================== 预约状态更新 ====================

@router.post("/{reservation_id}/accept")
def accept_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """打手接受预约"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    if reservation.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的预约")
    try:
        reservation_service.accept_reservation(db, reservation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "已接受预约"}


@router.post("/{reservation_id}/reject")
def reject_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """打手拒绝预约"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    if reservation.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的预约")
    try:
        reservation_service.reject_reservation(db, reservation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "已拒绝预约"}


@router.post("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_booster: Booster = Depends(get_current_booster),
):
    """打手取消已接受的预约"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约不存在")
    if reservation.booster_id != current_booster.id:
        raise HTTPException(status_code=403, detail="这不是你的预约")
    try:
        reservation_service.cancel_reservation(db, reservation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "已取消预约"}