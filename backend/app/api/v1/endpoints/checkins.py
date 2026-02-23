from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.core.security import decode_token
from app.crud.user import crud_user
from app.crud.checkin import crud_checkin
from app.crud.mood import crud_mood
from app.schemas.checkin import CheckinCreate, CheckoutCreate, CheckinResponse, DailyStatsResponse, MoodResponse
from app.models import User
from fastapi import Header, Depends

router = APIRouter(prefix="/api/v1/checkins", tags=["checkins"])


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/check-in", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
def check_in(
    request: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # สร้าง Mood ก่อน (ถ้ามี)
    mood = None
    if request.mood:
        mood = crud_mood.create(
            db,
            user_id=current_user.id,
            mood_level=request.mood.mood_level,
            emotion=request.mood.emotion,
            notes=request.mood.notes,
            # ไม่ส่ง checkin_id
        )

    # สร้าง Checkin พร้อม mood_id
    checkin = crud_checkin.create_checkin(
        db,
        user_id=current_user.id,
        location_latitude=request.location_latitude,
        location_longitude=request.location_longitude,
        location_name=request.location_name,
        notes=request.notes,
        goal_id=request.goal_id,
        mood_id=mood.id if mood else None   # ← เพิ่ม
    )

    if mood:
        checkin.mood = mood

    return checkin


@router.post("/check-out", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
def check_out(
    request: CheckoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a check-out record."""
    checkout = crud_checkin.create_checkout(
        db,
        user_id=current_user.id,
        notes=request.notes
    )
    
    # Add mood if provided
    if request.mood:
        mood = crud_mood.create(
            db,
            user_id=current_user.id,
            mood_level=request.mood.mood_level,
            emotion=request.mood.emotion,
            notes=request.mood.notes,
            checkin_id=checkout.id
        )
        checkout.mood = mood
    
    return checkout


@router.get("/today", response_model=DailyStatsResponse)
def get_today_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's check-in statistics."""
    today_checkins = crud_checkin.get_user_checkins_today(db, current_user.id)
    moods = crud_mood.get_user_moods(db, current_user.id, skip=0, limit=10)
    
    total_duration = 0
    is_checked_in = False
    
    for checkin in today_checkins:
        if checkin.status == "checked_in":
            is_checked_in = True
        if checkin.duration_minutes:
            total_duration += checkin.duration_minutes
    
    return {
        "total_checkins_today": len(today_checkins),
        "is_checked_in": is_checked_in,
        "latest_checkin": today_checkins[0] if today_checkins else None,
        "total_duration_minutes": total_duration,
        "mood_history": moods
    }


@router.get("", response_model=list[CheckinResponse])
def get_checkins(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's check-in history with pagination."""
    return crud_checkin.get_user_checkins(db, current_user.id, skip=skip, limit=limit)


@router.get("/{checkin_id}", response_model=CheckinResponse)
def get_checkin(
    checkin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific check-in record."""
    checkin = crud_checkin.get_by_id(db, checkin_id)
    if not checkin or checkin.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    return checkin


@router.patch("/{checkin_id}", response_model=CheckinResponse)
def update_checkin(
    checkin_id: UUID,
    request: CheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a check-in record."""
    checkin = crud_checkin.get_by_id(db, checkin_id)
    if not checkin or checkin.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    updated = crud_checkin.update(
        db,
        checkin,
        notes=request.notes,
        location_name=request.location_name
    )
    
    return updated


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(
    checkin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a check-in record."""
    checkin = crud_checkin.get_by_id(db, checkin_id)
    if not checkin or checkin.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    crud_checkin.delete(db, checkin)
    return None
