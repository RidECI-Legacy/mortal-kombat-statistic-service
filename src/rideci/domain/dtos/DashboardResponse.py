from pydantic import BaseModel
from typing import Dict, List, Any

class InstitutionalDashboard(BaseModel):
    status: str
    metadata: Dict[str, Any]
    results: List[Dict[str, Any]]