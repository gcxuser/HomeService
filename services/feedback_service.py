from typing import Optional, List, Dict
from HomeService.db.session import SessionLocal
from HomeService.db.models import OrderReview, Order, User, Worker
from sqlalchemy.orm import Session

class FeedbackService:
    def create_review(self, order_id: int, user_id: int, rating: int, content: str, tags: str = "") -> OrderReview:
        db: Session = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            worker_id = order.worker_id if order else None
            review = OrderReview(
                order_id=order_id,
                user_id=user_id,
                worker_id=worker_id,
                rating=rating,
                content=content,
                tags=tags,
            )
            db.add(review)
            db.commit()
            db.refresh(review)
            return review
        finally:
            db.close()

    def list_reviews(self, user_id: int = None, worker_id: int = None) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            query = db.query(OrderReview)
            if user_id:
                query = query.filter(OrderReview.user_id == user_id)
            if worker_id:
                query = query.filter(OrderReview.worker_id == worker_id)
            reviews = query.order_by(OrderReview.created_at.desc()).all()
            return [
                {
                    "id": review.id,
                    "order_id": review.order_id,
                    "user_id": review.user_id,
                    "worker_id": review.worker_id,
                    "rating": review.rating,
                    "content": review.content,
                    "tags": review.tags,
                    "created_at": review.created_at.isoformat(),
                }
                for review in reviews
            ]
        finally:
            db.close()
