from typing import List, Optional, Dict
from HomeService.db.session import SessionLocal
from HomeService.db.models import ServiceItem, ServiceCategory, ServicePackage
from sqlalchemy.orm import Session

class CatalogService:
    def list_service_items(self) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            items = db.query(ServiceItem).filter(ServiceItem.is_active == "active").all()
            return [self._to_dict(item) for item in items]
        finally:
            db.close()

    def get_service_item(self, item_id: int) -> Optional[Dict]:
        db: Session = SessionLocal()
        try:
            item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()
            return self._to_dict(item) if item else None
        finally:
            db.close()

    def search_service_items(self, keyword: str) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            lower_keyword = f"%{keyword.lower()}%"
            items = db.query(ServiceItem).filter(
                ServiceItem.name.ilike(lower_keyword) | ServiceItem.description.ilike(lower_keyword)
            ).all()
            return [self._to_dict(item) for item in items]
        finally:
            db.close()

    def list_categories(self) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            categories = db.query(ServiceCategory).all()
            return [{"id": category.id, "name": category.name, "description": category.description} for category in categories]
        finally:
            db.close()

    def create_category(self, name: str, description: str) -> ServiceCategory:
        db: Session = SessionLocal()
        category = ServiceCategory(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        db.close()
        return category

    def list_packages(self) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            packages = db.query(ServicePackage).all()
            return [self._package_to_dict(package) for package in packages]
        finally:
            db.close()

    def get_packages_for_item(self, item_id: int) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            packages = db.query(ServicePackage).filter(ServicePackage.service_item_id == item_id).all()
            return [self._package_to_dict(package) for package in packages]
        finally:
            db.close()

    def create_service_item(self, name: str, category: str, base_price: float, price_unit: str, estimated_duration: float, description: str) -> ServiceItem:
        db: Session = SessionLocal()
        item = ServiceItem(
            name=name,
            category=category,
            base_price=base_price,
            price_unit=price_unit,
            estimated_duration=estimated_duration,
            description=description,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        db.close()
        return item

    def create_package(self, service_item_id: int, name: str, included_scope: str, excluded_scope: str, base_price: float, estimated_duration: float, price_rule: str) -> ServicePackage:
        db: Session = SessionLocal()
        package = ServicePackage(
            service_item_id=service_item_id,
            name=name,
            included_scope=included_scope,
            excluded_scope=excluded_scope,
            base_price=base_price,
            estimated_duration=estimated_duration,
            price_rule=price_rule,
        )
        db.add(package)
        db.commit()
        db.refresh(package)
        db.close()
        return package

    def _to_dict(self, item: ServiceItem) -> Dict:
        return {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "base_price": item.base_price,
            "price_unit": item.price_unit,
            "estimated_duration": item.estimated_duration,
            "description": item.description,
        }

    def _package_to_dict(self, package: ServicePackage) -> Dict:
        return {
            "id": package.id,
            "service_item_id": package.service_item_id,
            "name": package.name,
            "included_scope": package.included_scope,
            "excluded_scope": package.excluded_scope,
            "base_price": package.base_price,
            "estimated_duration": package.estimated_duration,
            "price_rule": package.price_rule,
        }
