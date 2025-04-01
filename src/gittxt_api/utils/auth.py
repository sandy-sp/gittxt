from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException

limiter = Limiter(key_func=get_remote_address)

async def authenticate_request(request: Request, api_key: str):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=401, detail="Unauthorized")
