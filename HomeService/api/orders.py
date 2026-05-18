from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from HomeService.services.order_service import OrderService

router = APIRouter()
order_service = OrderService()

class OrderCreateRequest(BaseModel):
    user_id: int
    address_id: int
    service_item_id: int
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
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]

class RescheduleRequest(BaseModel):
    scheduled_start: datetime
    scheduled_end: datetime

class CancelRequest(BaseModel):
    reason: str = ""

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
        scheduled_start=order.scheduled_start,
        scheduled_end=order.scheduled_end,
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
        scheduled_start=order.scheduled_start,
        scheduled_end=order.scheduled_end,
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
        scheduled_start=order.scheduled_start,
        scheduled_end=order.scheduled_end,
    )

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, request: CancelRequest):
    order = order_service.cancel_order(order_id, request.reason)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or cannot be canceled")
    return {"order_id": order.id, "status": order.status}

@router.get("/user/{user_id}")
async def get_orders_by_user(user_id: int):
    orders = order_service.get_orders_by_user(user_id)
    return {"orders": [
        {
            "order_id": order.id,
            "status": order.status,
            "estimated_price": order.estimated_price,
            "final_price": order.final_price,
            "scheduled_start": order.scheduled_start,
            "scheduled_end": order.scheduled_end,
        }
        for order in orders
    ]}
