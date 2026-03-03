from pydantic import BaseModel
from typing import List

class AssignRoleRequest(BaseModel):
    role_names: List[str]

