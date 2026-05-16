from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from HomeService.config import settings

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    if request.username != settings.admin_username or request.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=settings.api_secret_key)
