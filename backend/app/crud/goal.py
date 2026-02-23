from sqlalchemy.orm import Session
from app.models import Goal
from uuid import UUID
import uuid


class CRUDGoal:
    def create(
        self,
        db: Session,
        user_id: UUID,
        title: str,
        description: str = None,
        priority: str = "medium"
    ) -> Goal:
        """Create a new goal."""
        goal = Goal(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            priority=priority
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal
    
    def get_by_id(self, db: Session, goal_id: UUID) -> Goal | None:
        """Get goal by ID."""
        return db.query(Goal).filter(Goal.id == goal_id).first()
    
    def get_user_goals(
        self,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> list[Goal]:
        """Get user's goals with pagination."""
        return db.query(Goal).filter(
            Goal.user_id == user_id
        ).order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_goals_by_completed(
        self,
        db: Session,
        user_id: UUID,
        is_completed: bool
    ) -> list[Goal]:
        """Get user's goals filtered by completion status."""
        return db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.is_completed == is_completed
        ).order_by(Goal.created_at.desc()).all()
    
    def update(self, db: Session, goal: Goal, **kwargs) -> Goal:
        """Update goal fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(goal, key):
                setattr(goal, key, value)
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal
    
    def delete(self, db: Session, goal: Goal) -> None:
        """Delete a goal."""
        db.delete(goal)
        db.commit()


crud_goal = CRUDGoal()
