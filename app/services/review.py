from sqlalchemy.orm import Session

from app.models import Order, Review


def create_review(
    db: Session,
    order_id: int,
    customer_id: int,
    booster_id: int,
    attitude_star: int,
    emotion_star: int,
    performance_star: int,
    content: str | None,
) -> Review:
    """客户提交评价"""
    review = Review(
        order_id=order_id,
        customer_id=customer_id,
        booster_id=booster_id,
        attitude_star=attitude_star,
        emotion_star=emotion_star,
        performance_star=performance_star,
        content=content,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews_by_customer(db: Session, customer_id: int) -> list[Review]:
    """获取客户的所有评价"""
    return db.query(Review).filter(Review.customer_id == customer_id).all()


def get_reviews_by_booster(db: Session, booster_id: int) -> list[Review]:
    """获取打手的所有评价"""
    return db.query(Review).filter(Review.booster_id == booster_id).all()


def reply_review(db: Session, review: Review, reply: str) -> Review:
    """打手回复评价"""
    review.reply = reply
    db.commit()
    db.refresh(review)
    return review