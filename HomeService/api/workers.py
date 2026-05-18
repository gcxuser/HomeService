from fastapi import APIRouter
from HomeService.services.worker_service import WorkerService

router = APIRouter()
worker_service = WorkerService()

@router.get("/")
async def list_workers():
    return {"workers": worker_service.list_workers()}

@router.get("/available")
async def available_workers(city: str, district: str, service_type: str):
    return {"workers": worker_service.find_workers(city, district, service_type)}
