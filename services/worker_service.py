from typing import List, Dict, Optional
from HomeService.db.session import SessionLocal
from HomeService.db.models import Worker, WorkerAvailability, WorkerSkill, ServiceItem
from sqlalchemy.orm import Session

class WorkerService:
    def list_workers(self) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            workers = db.query(Worker).all()
            return [self._to_dict(worker) for worker in workers]
        finally:
            db.close()

    def get_worker(self, worker_id: int) -> Optional[Dict]:
        db: Session = SessionLocal()
        try:
            worker = db.query(Worker).filter(Worker.id == worker_id).first()
            return self._to_dict(worker) if worker else None
        finally:
            db.close()

    def find_workers(self, city: str, district: str, service_type: str) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            query = db.query(Worker).filter(
                Worker.city == city,
                Worker.district == district,
                Worker.status == "active",
            )
            workers = query.order_by(Worker.rating.desc()).all()
            return [self._to_dict(worker) for worker in workers]
        finally:
            db.close()

    def find_workers_by_skill(self, city: str, district: str, service_item_id: int) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            skills = db.query(WorkerSkill).filter(WorkerSkill.service_item_id == service_item_id).all()
            worker_ids = [skill.worker_id for skill in skills]
            workers = db.query(Worker).filter(
                Worker.id.in_(worker_ids),
                Worker.city == city,
                Worker.district == district,
                Worker.status == "active",
            ).order_by(Worker.rating.desc()).all()
            return [self._to_dict(worker) for worker in workers]
        finally:
            db.close()

    def create_worker(self, name: str, city: str, district: str, status: str, rating: float, tags: str) -> Worker:
        db: Session = SessionLocal()
        worker = Worker(
            name=name,
            city=city,
            district=district,
            status=status,
            rating=rating,
            tags=tags,
        )
        db.add(worker)
        db.commit()
        db.refresh(worker)
        db.close()
        return worker

    def add_skill(self, worker_id: int, service_item_id: int, skill_level: str = "intermediate") -> WorkerSkill:
        db: Session = SessionLocal()
        skill = WorkerSkill(
            worker_id=worker_id,
            service_item_id=service_item_id,
            skill_level=skill_level,
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        db.close()
        return skill

    def get_availabilities(self, worker_id: int) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            records = db.query(WorkerAvailability).filter(WorkerAvailability.worker_id == worker_id).all()
            return [
                {
                    "id": record.id,
                    "available_date": record.available_date,
                    "start_time": record.start_time,
                    "end_time": record.end_time,
                    "status": record.status,
                }
                for record in records
            ]
        finally:
            db.close()

    def _to_dict(self, worker: Worker) -> Dict:
        return {
            "id": worker.id,
            "name": worker.name,
            "phone": worker.phone,
            "city": worker.city,
            "district": worker.district,
            "status": worker.status,
            "rating": worker.rating,
            "order_count": worker.order_count,
            "experience_years": worker.experience_years,
            "certificates": worker.certificates,
            "tags": worker.tags.split(",") if worker.tags else [],
        }

    def _to_dict(self, worker: Worker) -> Dict:
        return {
            "id": worker.id,
            "name": worker.name,
            "phone": worker.phone,
            "city": worker.city,
            "district": worker.district,
            "status": worker.status,
            "rating": worker.rating,
            "order_count": worker.order_count,
            "experience_years": worker.experience_years,
            "certificates": worker.certificates,
            "tags": worker.tags.split(",") if worker.tags else [],
        }
