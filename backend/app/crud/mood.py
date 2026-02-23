from sqlalchemy.orm import Session
from app.models import Mood
from uuid import UUID
import uuid


class CRUDMood:
    def create(
        self,
        db: Session,
        user_id: UUID,
        mood_level: int,
        emotion: str = None,
        notes: str = None,
        checkin_id: UUID = None
    ) -> Mood:
        """Create a new mood record."""
        mood = Mood(
            id=uuid.uuid4(),
            user_id=user_id,
            mood_level=mood_level,
            emotion=emotion,
            notes=notes,
            checkin_id=checkin_id
        )
        db.add(mood)
        db.commit()
        db.refresh(mood)
        return mood
    
    def get_by_id(self, db: Session, mood_id: UUID) -> Mood | None:
        """Get mood by ID."""
        return db.query(Mood).filter(Mood.id == mood_id).first()
    
    def get_user_moods(
        self,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Mood]:
        """Get user's mood records with pagination."""
        return db.query(Mood).filter(
            Mood.user_id == user_id
        ).order_by(Mood.created_at.desc()).offset(skip).limit(limit).all()


crud_mood = CRUDMood()
