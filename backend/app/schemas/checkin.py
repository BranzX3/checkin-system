from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class MoodCreate(BaseModel):
    mood_level: int = Field(..., ge=1, le=5)
    emotion: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "mood_level": 4,
                "emotion": "focused",
                "notes": "Feeling productive today"
            }
        }


class MoodResponse(BaseModel):
    id: UUID
    user_id: UUID
    mood_level: int
    emotion: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project report",
                "description": "Finish Q1 analysis",
                "priority": "high"
            }
        }


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None


class CheckinCreate(BaseModel):
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    location_name: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[MoodCreate] = None
    goal_id: Optional[UUID] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_latitude": 13.7563,
                "location_longitude": 100.5018,
                "location_name": "Office",
                "notes": "Starting work",
                "mood": {
                    "mood_level": 4,
                    "emotion": "focused"
                }
            }
        }


class CheckoutCreate(BaseModel):
    notes: Optional[str] = None
    mood: Optional[MoodCreate] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "notes": "Great day!",
                "mood": {
                    "mood_level": 5,
                    "emotion": "happy"
                }
            }
        }


class CheckinResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    timestamp: datetime
    location_latitude: Optional[float]
    location_longitude: Optional[float]
    location_name: Optional[str]
    notes: Optional[str]
    duration_minutes: Optional[int]
    mood: Optional[MoodResponse] = None
    goal_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DailyStatsResponse(BaseModel):
    total_checkins_today: int
    is_checked_in: bool
    latest_checkin: Optional[CheckinResponse] = None
    total_duration_minutes: int
    mood_history: list[MoodResponse] = []
