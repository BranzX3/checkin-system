from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from app.models import Checkin, Mood, Goal
from uuid import UUID
import uuid


class CRUDCheckin:
    def create_checkin(
        self, 
        db: Session, 
        user_id: UUID,
        location_latitude: float = None,
        location_longitude: float = None,
        location_name: str = None,
        notes: str = None,
        goal_id: UUID = None
    ) -> Checkin:
        """Create a new check-in record."""
        checkin = Checkin(
            id=uuid.uuid4(),
            user_id=user_id,
            status="checked_in",
            timestamp=datetime.utcnow(),
            location_latitude=location_latitude,
            location_longitude=location_longitude,
            location_name=location_name,
            notes=notes,
            goal_id=goal_id
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        return checkin
    
    def create_checkout(
        self,
        db: Session,
        user_id: UUID,
        notes: str = None
    ) -> Checkin:
        """Create a check-out record."""
        # Get the latest check-in for today
        today = datetime.utcnow().date()
        latest_checkin = db.query(Checkin).filter(
            and_(
                Checkin.user_id == user_id,
                Checkin.status == "checked_in",
                Checkin.timestamp >= datetime.combine(today, datetime.min.time())
            )
        ).order_by(Checkin.timestamp.desc()).first()
        
        duration_minutes = None
        if latest_checkin:
            duration = datetime.utcnow() - latest_checkin.timestamp
            duration_minutes = int(duration.total_seconds() / 60)
        
        checkout = Checkin(
            id=uuid.uuid4(),
            user_id=user_id,
            status="checked_out",
            timestamp=datetime.utcnow(),
            notes=notes,
            duration_minutes=duration_minutes
        )
        db.add(checkout)
        db.commit()
        db.refresh(checkout)
        return checkout
    
    def get_by_id(self, db: Session, checkin_id: UUID) -> Checkin | None:
        """Get check-in by ID."""
        return db.query(Checkin).filter(Checkin.id == checkin_id).first()
    
    def get_user_checkins_today(self, db: Session, user_id: UUID) -> list[Checkin]:
        """Get all check-ins for a user today."""
        today = datetime.utcnow().date()
        return db.query(Checkin).filter(
            and_(
                Checkin.user_id == user_id,
                Checkin.timestamp >= datetime.combine(today, datetime.min.time()),
                Checkin.timestamp < datetime.combine(today + timedelta(days=1), datetime.min.time())
            )
        ).order_by(Checkin.timestamp.desc()).all()
    
    def get_user_checkins(
        self, 
        db: Session, 
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> list[Checkin]:
        """Get user's check-ins with pagination."""
        return db.query(Checkin).filter(
            Checkin.user_id == user_id
        ).order_by(Checkin.timestamp.desc()).offset(skip).limit(limit).all()
    
    def is_checked_in(self, db: Session, user_id: UUID) -> bool:
        """Check if user is currently checked in."""
        today = datetime.utcnow().date()
        latest = db.query(Checkin).filter(
            and_(
                Checkin.user_id == user_id,
                Checkin.timestamp >= datetime.combine(today, datetime.min.time())
            )
        ).order_by(Checkin.timestamp.desc()).first()
        
        return latest and latest.status == "checked_in" if latest else False
    
    def get_latest_checkin(self, db: Session, user_id: UUID) -> Checkin | None:
        """Get the latest check-in for a user."""
        return db.query(Checkin).filter(
            Checkin.user_id == user_id
        ).order_by(Checkin.timestamp.desc()).first()
    
    def update(self, db: Session, checkin: Checkin, **kwargs) -> Checkin:
        """Update check-in fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(checkin, key):
                setattr(checkin, key, value)
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        return checkin
    
    def delete(self, db: Session, checkin: Checkin) -> None:
        """Delete a check-in."""
        db.delete(checkin)
        db.commit()


crud_checkin = CRUDCheckin()
