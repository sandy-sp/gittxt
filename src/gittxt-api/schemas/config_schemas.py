# gittxt-api/schemas/config_schemas.py
from pydantic import BaseModel
from typing import Optional

class UpdateConfigRequest(BaseModel):
    output_dir: Optional[str] = None
    logging_level: Optional[str] = None
