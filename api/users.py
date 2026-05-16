from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from HomeService.services.user_service import UserService
from HomeService.services.user_behavior_service import UserBehaviorService

router = APIRouter()
user_service = UserService()
behavior_service = UserBehaviorService()

class UserCreateRequest(BaseModel):
    name: str
    phone: str

class AddressCreateRequest(BaseModel):
    city: str
    district: str
    community: str
    detail_address: str
    remark: str = ""

@router.post("/", status_code=201)
async def create_user(request: UserCreateRequest):
    user = user_service.get_or_create_user(request.name, request.phone)
    return {"user_id": user.id, "name": user.name, "phone": user.phone}

@router.get("/{user_id}")
async def get_user(user_id: int):
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id, "name": user.name, "phone": user.phone}

@router.post("/{user_id}/addresses")
async def add_address(user_id: int, request: AddressCreateRequest):
    address = user_service.add_address(
        user_id=user_id,
        city=request.city,
        district=request.district,
        community=request.community,
        detail_address=request.detail_address,
        remark=request.remark,
    )
    return {"address_id": address.id}

@router.get("/{user_id}/addresses")
async def list_addresses(user_id: int):
    addresses = user_service.get_addresses(user_id)
    return {"addresses": [
        {
            "id": item.id,
            "city": item.city,
            "district": item.district,
            "community": item.community,
            "detail_address": item.detail_address,
            "remark": item.remark,
        }
        for item in addresses
    ]}

@router.get("/{user_id}/recommendations")
async def get_recommendations(user_id: int):
    profile = behavior_service.get_user_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    recommendations = behavior_service.recommend_repeat_service(user_id)
    return {
        "user": profile,
        "recommendation": recommendations,
    }

@router.get("/{user_id}/analytics")
async def get_user_analytics(user_id: int):
    profile = behavior_service.get_user_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    analytics = behavior_service.analyze_user_behavior(user_id)
    return {
        "user": profile,
        "analytics": analytics,
    }
