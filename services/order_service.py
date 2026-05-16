from typing import Optional
from HomeService.db.session import SessionLocal
from HomeService.db.models import Order, OrderStatusLog, Worker, UserAddress, User
from HomeService.services.worker_service import WorkerService
from HomeService.services.dispatch_service import DispatchService
from HomeService.services.mcp_service import MCPService
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class OrderService:
    def __init__(self):
        self.worker_service = WorkerService()
        self.dispatch_service = DispatchService()
        self.mcp_service = MCPService()

    def create_order(
        self,
        user_id: int,
        service_item_id: int,
        address_id: int,
        scheduled_start: datetime,
        scheduled_end: datetime,
        estimated_price: float,
        final_price: float,
        remark: str = "",
    ) -> Order:
        db: Session = SessionLocal()
        try:
            worker = self.dispatch_service.match_worker(address_id, service_item_id, scheduled_start, scheduled_end)
            worker_id = worker.id if worker else None
            order = Order(
                user_id=user_id,
                service_item_id=service_item_id,
                address_id=address_id,
                worker_id=worker_id,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                estimated_price=estimated_price,
                final_price=final_price,
                status="confirmed",
                payment_status="pending",
                remark=remark,
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            self._log_order(db, order.id, "pending", order.status, "system", "订单创建")
            if worker:
                worker.order_count += 1
                db.add(worker)
                self.dispatch_service.reserve_availability(worker.id, scheduled_start, scheduled_end)
                db.commit()

            self._sync_calendar_and_notify(db, order)
            return order
        finally:
            db.close()

    def _sync_calendar_and_notify(self, db: Session, order: Order) -> None:
        if order.user_id and order.scheduled_start and order.scheduled_end:
            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                self.mcp_service.schedule_calendar_event(
                    order.user_id,
                    order.id,
                    f"家政服务预约：{order.service_item.name if order.service_item else '服务'}",
                    order.scheduled_start,
                    order.scheduled_end,
                    f"服务地址：{order.address.city if order.address else ''} {order.address.district if order.address else ''} {order.address.detail_address if order.address else ''}",
                )
                if user.phone:
                    self.mcp_service.send_notification(
                        order.user_id,
                        user.phone,
                        "家政服务预约已确认",
                        f"您的订单 {order.id} 已确认，服务时间 {order.scheduled_start.isoformat()} - {order.scheduled_end.isoformat()}。",
                    )

    def get_order(self, order_id: int):
        db: Session = SessionLocal()
        try:
            return db.query(Order).filter(Order.id == order_id).first()
        finally:
            db.close()

    def get_orders_by_user(self, user_id: int):
        db: Session = SessionLocal()
        try:
            return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
        finally:
            db.close()

    def reschedule_order(self, order_id: int, scheduled_start: datetime, scheduled_end: datetime):
        db: Session = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order is None or order.status not in ["confirmed", "pending"]:
                return None
            if not self._can_reschedule(order):
                return None
            old_status = order.status
            order.scheduled_start = scheduled_start
            order.scheduled_end = scheduled_end
            order.status = "rescheduled"
            db.add(order)
            self._log_order(db, order.id, old_status, order.status, "system", "改约")
            db.commit()
            db.refresh(order)
            return order
        finally:
            db.close()

    def cancel_order(self, order_id: int, reason: str = ""):
        db: Session = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order is None or order.status in ["cancelled", "completed"]:
                return None
            if not self._can_cancel(order):
                return None
            old_status = order.status
            order.status = "cancelled"
            db.add(order)
            self._log_order(db, order.id, old_status, order.status, "system", f"取消订单: {reason}")
            db.commit()
            db.refresh(order)
            return order
        finally:
            db.close()

    def _can_reschedule(self, order: Order) -> bool:
        if order.scheduled_start is None:
            return False
        return order.scheduled_start - datetime.utcnow() > timedelta(hours=12)

    def _can_cancel(self, order: Order) -> bool:
        if order.scheduled_start is None:
            return True
        delta = order.scheduled_start - datetime.utcnow()
        return delta > timedelta(hours=2)

    def _log_order(self, db: Session, order_id: int, from_status: str, to_status: str, operator_type: str, remark: str) -> None:
        log = OrderStatusLog(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            operator_type=operator_type,
            remark=remark,
        )
        db.add(log)
        db.commit()
