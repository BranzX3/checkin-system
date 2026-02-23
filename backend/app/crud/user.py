from sqlalchemy.orm import Session
from app.models import User
from app.core.security import hash_password, verify_password
from uuid import UUID


class CRUDUser:
    def create(self, db: Session, email: str, password: str, full_name: str = None) -> User:
        """Create a new user."""
        hashed_password = hash_password(password)
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_by_email(self, db: Session, email: str) -> User | None:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, db: Session, user_id: UUID) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def authenticate(self, db: Session, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update(self, db: Session, user: User, **kwargs) -> User:
        """Update user fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active


crud_user = CRUDUser()
