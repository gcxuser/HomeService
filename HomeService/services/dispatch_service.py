from typing import Optional, Dict, List
from HomeService.db.session import SessionLocal
from HomeService.db.models import Worker, WorkerAvailability, UserAddress, Order, WorkerSkill, ServiceItem
from sqlalchemy.orm import Session
from datetime import datetime

class DispatchService:
    def __init__(self):
        pass

    def match_worker(self, address_id: int, service_item_id: int, scheduled_start: datetime, scheduled_end: datetime) -> Optional[Worker]:
        db: Session = SessionLocal()
        try:
            address = db.query(UserAddress).filter(UserAddress.id == address_id).first()
            if address is None:
                return None
            service_item = db.query(ServiceItem).filter(ServiceItem.id == service_item_id).first()
            if service_item is None:
                return None
            candidates = db.query(Worker).filter(
                Worker.city == address.city,
                Worker.district == address.district,
                Worker.status == "active",
            ).all()
            if not candidates:
                return None
            scored: List[Dict] = []
            for worker in candidates:
                score = worker.rating
                skill = db.query(WorkerSkill).filter(
                    WorkerSkill.worker_id == worker.id,
                    WorkerSkill.service_item_id == service_item.id,
                ).first()
                if skill:
                    score += 1.5
                availability_match = db.query(WorkerAvailability).filter(
                    WorkerAvailability.worker_id == worker.id,
                    WorkerAvailability.available_date == scheduled_start.strftime("%Y-%m-%d"),
                    WorkerAvailability.start_time <= scheduled_start.strftime("%H:%M"),
                    WorkerAvailability.end_time >= scheduled_end.strftime("%H:%M"),
                    WorkerAvailability.status == "open",
                ).first()
                if availability_match:
                    score += 1.0
                scored.append({"worker": worker, "score": score})
            scored.sort(key=lambda item: item["score"], reverse=True)
            return scored[0]["worker"] if scored else None
        finally:
            db.close()

    def reserve_availability(self, worker_id: int, scheduled_start: datetime, scheduled_end: datetime) -> None:
        db: Session = SessionLocal()
        try:
            date_key = scheduled_start.strftime("%Y-%m-%d")
            slot = db.query(WorkerAvailability).filter(
                WorkerAvailability.worker_id == worker_id,
                WorkerAvailability.available_date == date_key,
                WorkerAvailability.start_time <= scheduled_start.strftime("%H:%M"),
                WorkerAvailability.end_time >= scheduled_end.strftime("%H:%M"),
                WorkerAvailability.status == "open",
            ).first()
            if slot:
                slot.status = "reserved"
                db.add(slot)
                db.commit()
        finally:
            db.close()
