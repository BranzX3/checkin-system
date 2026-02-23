from sqlalchemy.orm import Session
from app.models import Team, TeamMember, User
from uuid import UUID
import uuid
import random
import string


class CRUDTeam:
    def create(
        self,
        db: Session,
        name: str,
        created_by: UUID,
        description: str = None
    ) -> Team:
        """Create a new team."""
        code = self._generate_team_code()
        team = Team(
            id=uuid.uuid4(),
            name=name,
            code=code,
            description=description,
            created_by=created_by
        )
        db.add(team)
        db.commit()
        
        # Add creator as team owner
        self.add_member(db, team.id, created_by, "owner")
        
        db.refresh(team)
        return team
    
    def _generate_team_code(self) -> str:
        """Generate a unique team code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def get_by_id(self, db: Session, team_id: UUID) -> Team | None:
        """Get team by ID."""
        return db.query(Team).filter(Team.id == team_id).first()
    
    def get_by_code(self, db: Session, code: str) -> Team | None:
        """Get team by code."""
        return db.query(Team).filter(Team.code == code).first()
    
    def get_user_teams(self, db: Session, user_id: UUID) -> list[Team]:
        """Get all teams for a user."""
        return db.query(Team).join(TeamMember).filter(
            TeamMember.user_id == user_id,
            Team.is_active == True
        ).all()
    
    def add_member(
        self,
        db: Session,
        team_id: UUID,
        user_id: UUID,
        role: str = "member"
    ) -> TeamMember:
        """Add a member to a team."""
        member = TeamMember(
            id=uuid.uuid4(),
            team_id=team_id,
            user_id=user_id,
            role=role
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    def get_team_members(self, db: Session, team_id: UUID) -> list[TeamMember]:
        """Get all members of a team."""
        return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    
    def remove_member(
        self,
        db: Session,
        team_id: UUID,
        user_id: UUID
    ) -> None:
        """Remove a member from a team."""
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        if member:
            db.delete(member)
            db.commit()
    
    def get_member_role(
        self,
        db: Session,
        team_id: UUID,
        user_id: UUID
    ) -> str | None:
        """Get member's role in a team."""
        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        return member.role if member else None
    
    def is_member(
        self,
        db: Session,
        team_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user is a member of team."""
        return db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first() is not None


crud_team = CRUDTeam()
