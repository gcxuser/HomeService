from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from HomeService.utils.security import admin_required
from HomeService.services.catalog_service import CatalogService
from HomeService.services.worker_service import WorkerService
from HomeService.services.availability_service import AvailabilityService

router = APIRouter()
router_service = CatalogService()
worker_service = WorkerService()
availability_service = AvailabilityService()

class ServiceItemRequest(BaseModel):
    name: str
    category: str
    base_price: float
    price_unit: str
    estimated_duration: float
    description: str = ""

class CategoryRequest(BaseModel):
    name: str
    description: str = ""

class PackageRequest(BaseModel):
    service_item_id: int
    name: str
    included_scope: str
    excluded_scope: str
    base_price: float
    estimated_duration: float
    price_rule: str = ""

class WorkerRequest(BaseModel):
    name: str
    city: str
    district: str
    status: str = "active"
    rating: float = 4.8
    tags: list[str] = []

class AvailabilityRequest(BaseModel):
    worker_id: int
    city: str
    district: str
    available_date: str
    start_time: str
    end_time: str

@router.post("/services", dependencies=[Depends(admin_required)])
async def create_service(request: ServiceItemRequest):
    item = router_service.create_service_item(
        request.name,
        request.category,
        request.base_price,
        request.price_unit,
        request.estimated_duration,
        request.description,
    )
    return {"service_item_id": item.id}

@router.get("/services", dependencies=[Depends(admin_required)])
async def list_services():
    return {"services": router_service.list_service_items()}

@router.post("/categories", dependencies=[Depends(admin_required)])
async def create_category(request: CategoryRequest):
    category = router_service.create_category(request.name, request.description)
    return {"category_id": category.id}

@router.get("/categories", dependencies=[Depends(admin_required)])
async def list_categories():
    return {"categories": router_service.list_categories()}

@router.post("/packages", dependencies=[Depends(admin_required)])
async def create_package(request: PackageRequest):
    package = router_service.create_package(
        request.service_item_id,
        request.name,
        request.included_scope,
        request.excluded_scope,
        request.base_price,
        request.estimated_duration,
        request.price_rule,
    )
    return {"package_id": package.id}

@router.get("/packages/{service_item_id}", dependencies=[Depends(admin_required)])
async def list_packages(service_item_id: int):
    packages = router_service.get_packages_for_item(service_item_id)
    return {"packages": packages}

@router.post("/workers", dependencies=[Depends(admin_required)])
async def create_worker(request: WorkerRequest):
    worker = worker_service.create_worker(
        request.name,
        request.city,
        request.district,
        request.status,
        request.rating,
        ",".join(request.tags),
    )
    return {"worker_id": worker.id}

@router.post("/workers/availability", dependencies=[Depends(admin_required)])
async def add_availability(request: AvailabilityRequest):
    availability = availability_service.add_availability(
        worker_id=request.worker_id,
        city=request.city,
        district=request.district,
        available_date=request.available_date,
        start_time=request.start_time,
        end_time=request.end_time,
    )
    return {"availability_id": availability.id}
