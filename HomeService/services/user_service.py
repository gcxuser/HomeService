from typing import Optional
from HomeService.db.session import SessionLocal
from HomeService.db.models import User, UserAddress
from sqlalchemy.orm import Session

class UserService:
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        db: Session = SessionLocal()
        try:
            return db.query(User).filter(User.phone == phone).first()
        finally:
            db.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        db: Session = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    def create_user(self, name: str, phone: str) -> User:
        db: Session = SessionLocal()
        user = User(name=name, phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

    def get_or_create_user(self, name: str, phone: str) -> User:
        existing = self.get_user_by_phone(phone)
        if existing:
            if name and existing.name != name:
                db: Session = SessionLocal()
                try:
                    existing.name = name
                    db.add(existing)
                    db.commit()
                    db.refresh(existing)
                finally:
                    db.close()
            return existing
        return self.create_user(name=name or "用户", phone=phone)

    def add_address(self, user_id: int, city: str, district: str, community: str, detail_address: str, remark: str = "") -> UserAddress:
        db: Session = SessionLocal()
        address = UserAddress(
            user_id=user_id,
            city=city,
            district=district,
            community=community,
            detail_address=detail_address,
            remark=remark,
        )
        db.add(address)
        db.commit()
        db.refresh(address)
        db.close()
        return address

    def get_addresses(self, user_id: int):
        db: Session = SessionLocal()
        try:
            return db.query(UserAddress).filter(UserAddress.user_id == user_id).all()
        finally:
            db.close()
