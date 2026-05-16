import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from HomeService.config import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_api_key(api_key_header_value: str = Security(api_key_header)) -> str:
    if not api_key_header_value:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not api_key_header_value.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    token = api_key_header_value.split(" ", 1)[1]
    if not secrets.compare_digest(token, settings.api_secret_key):
        raise HTTPException(status_code=403, detail="Invalid API token")
    return token

async def admin_required(api_key: str = Depends(get_api_key)) -> bool:
    return True
