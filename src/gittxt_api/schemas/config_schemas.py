from pydantic import BaseModel
from typing import Optional

class UpdateConfigRequest(BaseModel):
    output_dir: Optional[str] = None
    logging_level: Optional[str] = None
    output_format: Optional[str] = None 
    file_types: Optional[str] = None  
    auto_zip: Optional[bool] = None  