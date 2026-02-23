from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.core.security import decode_token
from app.crud.user import crud_user
from app.crud.team import crud_team
from app.crud.checkin import crud_checkin
from app.schemas.team import TeamCreate, TeamResponse, TeamDetailResponse, TeamJoinRequest
from app.models import User

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


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


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team."""
    team = crud_team.create(
        db,
        name=request.name,
        description=request.description,
        created_by=current_user.id
    )
    
    return team


@router.get("", response_model=list[TeamResponse])
def get_user_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all teams for the current user."""
    return crud_team.get_user_teams(db, current_user.id)


@router.get("/{team_id}", response_model=TeamDetailResponse)
def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team details with member list."""
    team = crud_team.get_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user is a member
    if not crud_team.is_member(db, team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team"
        )
    
    members = crud_team.get_team_members(db, team_id)
    
    return {
        **team.__dict__,
        "members": members
    }


@router.post("/join", response_model=TeamResponse)
def join_team(
    request: TeamJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a team using team code."""
    team = crud_team.get_by_code(db, request.team_code)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if already a member
    if crud_team.is_member(db, team.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this team"
        )
    
    # Add user to team
    crud_team.add_member(db, team.id, current_user.id, role="member")
    
    return team


@router.post("/{team_id}/members/{user_id}/remove", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from a team (team owners only)."""
    team = crud_team.get_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if requester is owner
    requester_role = crud_team.get_member_role(db, team_id, current_user.id)
    if requester_role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owners can remove members"
        )
    
    crud_team.remove_member(db, team_id, user_id)
    return None
