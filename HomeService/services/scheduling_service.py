from typing import List
from datetime import datetime
from HomeService.db.session import SessionLocal
from HomeService.db.models import WorkerAvailability
from sqlalchemy.orm import Session

class SchedulingService:
    def get_available_slots(self, city: str, district: str, service_type: str, preferred_date: str) -> List[str]:
        db: Session = SessionLocal()
        try:
            records = db.query(WorkerAvailability).filter(
                WorkerAvailability.city == city,
                WorkerAvailability.district == district,
                WorkerAvailability.available_date == preferred_date,
                WorkerAvailability.status == "open",
            ).all()
            if not records:
                return [f"{preferred_date} 暂无可预约时段，建议提前24小时预约。"]
            slots = []
            for record in records:
                slots.append(f"{record.available_date} {record.start_time}-{record.end_time}")
            return slots
        finally:
            db.close()

    def is_slot_available(self, scheduled_start: datetime, scheduled_end: datetime) -> bool:
        return scheduled_start < scheduled_end
