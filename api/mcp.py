from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from HomeService.services.mcp_service import MCPService

router = APIRouter()
mcp_service = MCPService()

class AddressLocateRequest(BaseModel):
    city: str
    district: str
    community: str = ""
    detail_address: str = ""

class CalendarEventRequest(BaseModel):
    user_id: int
    order_id: int
    title: str
    start: datetime
    end: datetime
    description: str = ""

class NotificationRequest(BaseModel):
    user_id: int
    phone: str
    title: str
    message: str

@router.post("/locate")
async def locate_address(request: AddressLocateRequest):
    return mcp_service.get_location(
        request.city, request.district, request.community, request.detail_address
    )

@router.post("/calendar/schedule")
async def schedule_event(request: CalendarEventRequest):
    return mcp_service.schedule_calendar_event(
        request.user_id,
        request.order_id,
        request.title,
        request.start,
        request.end,
        request.description,
    )

@router.post("/notify")
async def notify_user(request: NotificationRequest):
    return mcp_service.send_notification(
        request.user_id,
        request.phone,
        request.title,
        request.message,
    )
