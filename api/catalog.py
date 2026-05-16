from fastapi import APIRouter, HTTPException
from HomeService.services.catalog_service import CatalogService

router = APIRouter()
catalog_service = CatalogService()

@router.get("/items")
async def list_items():
    return {"services": catalog_service.list_service_items()}

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = catalog_service.get_service_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Service item not found")
    return item

@router.get("/search")
async def search_items(q: str):
    return {"services": catalog_service.search_service_items(q)}
