from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from HomeService.agents.router_agent import RouterAgent

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    intent: str
    reply: str
    metadata: dict = {}

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    agent = RouterAgent()
    try:
        result = agent.route(request.user_id, request.message)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
