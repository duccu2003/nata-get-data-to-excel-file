from pydantic import BaseModel
from typing import Dict, Optional

class TemplateData(BaseModel):
    replacements: Optional[Dict[str, str]] = None