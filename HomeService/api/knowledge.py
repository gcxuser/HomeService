from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from HomeService.services.knowledge_service import KnowledgeService

router = APIRouter()

class KnowledgeUploadRequest(BaseModel):
    title: str
    doc_type: str
    service_type: str
    city: str
    content: str

@router.post("/upload")
async def upload_knowledge(request: KnowledgeUploadRequest):
    knowledge_service = KnowledgeService()
    doc = knowledge_service.create_document(
        title=request.title,
        doc_type=request.doc_type,
        service_type=request.service_type,
        city=request.city,
        content=request.content,
    )
    return {"id": doc.id, "message": "文档已上传"}

@router.get("/search")
async def search_knowledge(q: str):
    knowledge_service = KnowledgeService()
    return {"documents": knowledge_service.search_documents(q)}

@router.get("/list")
async def list_knowledge():
    knowledge_service = KnowledgeService()
    return {"documents": knowledge_service.list_documents()}

@router.get("/{doc_id}")
async def get_knowledge(doc_id: int):
    knowledge_service = KnowledgeService()
    doc = knowledge_service.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Knowledge document not found")
    return doc
