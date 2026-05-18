from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from HomeService.services.pricing_service import PricingService
from HomeService.services.scheduling_service import SchedulingService
from HomeService.services.order_service import OrderService

router = APIRouter()

class QuoteRequest(BaseModel):
    service_type: str
    area: float
    extras: dict = {}

class QuoteResponse(BaseModel):
    estimated_price: float
    estimated_duration: float
    note: str

class CheckSlotsRequest(BaseModel):
    city: str
    district: str
    service_type: str
    preferred_date: str

class OrderCreateRequest(BaseModel):
    user_id: int
    service_item_id: int
    address_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    estimated_price: float
    final_price: float
    remark: str = ""

class OrderResponse(BaseModel):
    order_id: int
    status: str
    estimated_price: float
    final_price: float

class RescheduleRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime

class CancelRequest(BaseModel):
    reason: str = ""

pricing_service = PricingService()
scheduling_service = SchedulingService()
order_service = OrderService()

@router.post("/quote", response_model=QuoteResponse)
async def quote(request: QuoteRequest):
    estimate = pricing_service.estimate_price(request.service_type, request.area, request.extras)
    return QuoteResponse(
        estimated_price=estimate["price"],
        estimated_duration=estimate["duration"],
        note=estimate["note"]
    )

@router.post("/check-slots")
async def check_slots(request: CheckSlotsRequest):
    slots = scheduling_service.get_available_slots(
        request.city, request.district, request.service_type, request.preferred_date
    )
    return {"available_slots": slots}

@router.post("/", response_model=OrderResponse)
async def create_order(request: OrderCreateRequest):
    order = order_service.create_order(
        request.user_id,
        request.service_item_id,
        request.address_id,
        request.scheduled_start,
        request.scheduled_end,
        request.estimated_price,
        request.final_price,
        request.remark,
    )
    return OrderResponse(
        order_id=order.id,
        status=order.status,
        estimated_price=order.estimated_price,
        final_price=order.final_price,
    )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(
        order_id=order.id,
        status=order.status,
        estimated_price=order.estimated_price,
        final_price=order.final_price,
    )

@router.post("/{order_id}/reschedule", response_model=OrderResponse)
async def reschedule_order(order_id: int, request: RescheduleRequest):
    order = order_service.reschedule_order(order_id, request.scheduled_start, request.scheduled_end)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or cannot be rescheduled")
    return OrderResponse(
        order_id=order.id,
        status=order.status,
        estimated_price=order.estimated_price,
        final_price=order.final_price,
    )

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, request: CancelRequest):
    order = order_service.cancel_order(order_id, request.reason)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or cannot be canceled")
    return {"order_id": order.id, "status": order.status}
