from typing import List
from HomeService.db.session import SessionLocal
from HomeService.db.models import WorkerAvailability
from sqlalchemy.orm import Session

class AvailabilityService:
    def get_available_slots(self, city: str, district: str, service_type: str, preferred_date: str) -> List[str]:
        db: Session = SessionLocal()
        try:
            records = db.query(WorkerAvailability).filter(
                WorkerAvailability.city == city,
                WorkerAvailability.district == district,
                WorkerAvailability.available_date == preferred_date,
                WorkerAvailability.status == "open",
            ).all()
            slots = [f"{record.available_date} {record.start_time}-{record.end_time}" for record in records]
            return slots
        finally:
            db.close()

    def add_availability(self, worker_id: int, city: str, district: str, available_date: str, start_time: str, end_time: str) -> WorkerAvailability:
        db: Session = SessionLocal()
        availability = WorkerAvailability(
            worker_id=worker_id,
            city=city,
            district=district,
            available_date=available_date,
            start_time=start_time,
            end_time=end_time,
            status="open",
        )
        db.add(availability)
        db.commit()
        db.refresh(availability)
        db.close()
        return availability
