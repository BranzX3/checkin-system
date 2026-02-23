from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TeamMemberResponse(BaseModel):
    user_id: UUID
    role: str
    joined_at: datetime
    
    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Development Team",
                "description": "Backend developers"
            }
        }


class TeamResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str]
    created_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    members: List[TeamMemberResponse] = []


class TeamInviteRequest(BaseModel):
    email: str
    role: Optional[str] = "member"


class TeamJoinRequest(BaseModel):
    team_code: str
