from typing import Dict, List, Optional
from datetime import datetime
from HomeService.db.session import SessionLocal
from HomeService.db.models import Order, ServiceItem, OrderReview, User
from sqlalchemy.orm import Session

class UserBehaviorService:
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            return {
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "member_level": user.member_level,
                "orders_count": len(user.orders),
                "joined_at": user.created_at.isoformat(),
            }
        finally:
            db.close()

    def get_user_orders(self, user_id: int) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
            return [self._order_to_dict(order) for order in orders]
        finally:
            db.close()

    def recommend_repeat_service(self, user_id: int) -> Dict:
        db: Session = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
            if not orders:
                return {
                    "recommendation": "您还没有预约记录，欢迎先体验我们的日常保洁或深度保洁服务。",
                    "reasons": ["首次预约优惠", "可预约家庭清洁套餐"],
                }

            last_order = orders[0]
            service_name = last_order.service_item.name if last_order.service_item else "家政服务"
            repeat_interval = "一个月后" if last_order.status == "completed" else "请尽快确认下次服务时间"
            summary = f"您最近一次预约的是{service_name}，我们建议您{repeat_interval}再次安排维护。"
            reasons = [
                f"您对{service_name}已有使用记录，继续预约更省心",
                "系统智能匹配同区域优质师傅",
                "可同步到日历并给您发送服务提醒",
            ]
            if len(orders) >= 3:
                reasons.append("根据历史记录，您可能对长期套餐更感兴趣")
            return {
                "recommendation": summary,
                "reasons": reasons,
                "last_order": self._order_to_dict(last_order),
            }
        finally:
            db.close()

    def analyze_user_behavior(self, user_id: int) -> Dict:
        db: Session = SessionLocal()
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).all()
            if not orders:
                return {"message": "暂无行为数据，欢迎先创建订单。"}

            service_counts: Dict[str, int] = {}
            completed_orders = 0
            for order in orders:
                service_name = order.service_item.name if order.service_item else "未知服务"
                service_counts[service_name] = service_counts.get(service_name, 0) + 1
                if order.status == "completed":
                    completed_orders += 1

            frequent_service = max(service_counts.items(), key=lambda x: x[1])[0]
            return {
                "total_orders": len(orders),
                "completed_orders": completed_orders,
                "frequent_service": frequent_service,
                "service_counts": service_counts,
                "user_value": "高" if completed_orders >= 3 else "中" if completed_orders >= 1 else "低",
            }
        finally:
            db.close()

    def _order_to_dict(self, order: Order) -> Dict:
        return {
            "order_id": order.id,
            "service_item": order.service_item.name if order.service_item else None,
            "status": order.status,
            "scheduled_start": order.scheduled_start.isoformat() if order.scheduled_start else None,
            "scheduled_end": order.scheduled_end.isoformat() if order.scheduled_end else None,
            "final_price": order.final_price,
            "created_at": order.created_at.isoformat(),
        }
