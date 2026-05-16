from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), unique=True, nullable=False)
    member_level = Column(String(32), default="standard")
    created_at = Column(DateTime, default=datetime.utcnow)
    addresses = relationship("UserAddress", back_populates="user")
    orders = relationship("Order", back_populates="user")

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city = Column(String(64), nullable=False)
    district = Column(String(64), nullable=False)
    community = Column(String(128), nullable=True)
    detail_address = Column(String(256), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    has_elevator = Column(String(32), nullable=True)
    parking_info = Column(String(128), nullable=True)
    remark = Column(Text, nullable=True)
    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")

class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    service_items = relationship("ServiceItem", back_populates="category_obj")

class ServiceItem(Base):
    __tablename__ = "service_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=True)
    category = Column(String(64), nullable=True)
    base_price = Column(Float, nullable=False, default=0.0)
    price_unit = Column(String(32), nullable=False, default="per_hour")
    estimated_duration = Column(Float, nullable=False, default=1.0)
    description = Column(Text, nullable=True)
    is_active = Column(String(32), nullable=False, default="active")
    category_obj = relationship("ServiceCategory", back_populates="service_items")
    packages = relationship("ServicePackage", back_populates="service_item")
    skills = relationship("WorkerSkill", back_populates="service_item")
    orders = relationship("Order", back_populates="service_item")

class ServicePackage(Base):
    __tablename__ = "service_packages"

    id = Column(Integer, primary_key=True, index=True)
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)
    name = Column(String(128), nullable=False)
    included_scope = Column(Text, nullable=True)
    excluded_scope = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False, default=0.0)
    estimated_duration = Column(Float, nullable=False, default=1.0)
    price_rule = Column(Text, nullable=True)
    service_item = relationship("ServiceItem", back_populates="packages")

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=True)
    city = Column(String(64), nullable=True)
    district = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    rating = Column(Float, nullable=False, default=4.8)
    order_count = Column(Integer, nullable=False, default=0)
    tags = Column(String(256), nullable=True)
    experience_years = Column(Integer, nullable=False, default=1)
    certificates = Column(Text, nullable=True)
    availabilities = relationship("WorkerAvailability", back_populates="worker")
    skills = relationship("WorkerSkill", back_populates="worker")
    orders = relationship("Order", back_populates="worker")

class WorkerSkill(Base):
    __tablename__ = "worker_skills"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)
    skill_level = Column(String(32), nullable=False, default="intermediate")
    worker = relationship("Worker", back_populates="skills")
    service_item = relationship("ServiceItem", back_populates="skills")

class WorkerAvailability(Base):
    __tablename__ = "worker_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    city = Column(String(64), nullable=False)
    district = Column(String(64), nullable=False)
    available_date = Column(String(32), nullable=False)
    start_time = Column(String(16), nullable=False)
    end_time = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False, default="open")
    worker = relationship("Worker", back_populates="availabilities")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("user_addresses.id"), nullable=True)
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    estimated_price = Column(Float, nullable=False, default=0.0)
    final_price = Column(Float, nullable=False, default=0.0)
    status = Column(String(32), nullable=False, default="pending")
    payment_status = Column(String(32), nullable=False, default="unpaid")
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    address = relationship("UserAddress", back_populates="orders")
    service_item = relationship("ServiceItem", back_populates="orders")
    worker = relationship("Worker", back_populates="orders")
    logs = relationship("OrderStatusLog", back_populates="order")

class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    from_status = Column(String(32), nullable=False)
    to_status = Column(String(32), nullable=False)
    operator_type = Column(String(64), nullable=False, default="system")
    operator_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    remark = Column(Text, nullable=True)
    order = relationship("Order", back_populates="logs")

class OrderReview(Base):
    __tablename__ = "order_reviews"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    rating = Column(Integer, nullable=False, default=5)
    content = Column(Text, nullable=True)
    tags = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    doc_type = Column(String(64), nullable=False)
    service_type = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
