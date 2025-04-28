from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


def current_utc_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class ApiResponse(BaseModel):
    status: str = Field(default="success", example="success")
    message: Optional[str] = Field(default="OK", example="Scan completed successfully.")
    data: Optional[Union[dict, list]] = None
    timestamp: str = Field(default_factory=current_utc_iso)


class ErrorResponse(BaseModel):
    status: str = Field(default="error", example="error")
    error: str = Field(example="Internal Server Error")
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=current_utc_iso)
