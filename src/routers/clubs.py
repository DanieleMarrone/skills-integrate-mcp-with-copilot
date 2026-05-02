"""
Club and membership management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
import crud
from schemas import ClubCreate, ClubResponse, MembershipCreate, MembershipResponse, MembershipUpdate
from security import get_current_user, get_current_admin

router = APIRouter(prefix="/clubs", tags=["clubs"])


@router.get("", response_model=list[ClubResponse])
def list_clubs(
    category: str = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all clubs"""
    query = db.query(crud.Club)
    
    if category:
        query = query.filter(crud.Club.category == category)
    
    clubs = query.offset(skip).limit(limit).all()
    return clubs


@router.get("/{club_id}", response_model=ClubResponse)
def get_club(club_id: int, db: Session = Depends(get_db)):
    """Get club details"""
    club = crud.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    return club


@router.post("", response_model=ClubResponse)
def create_club(
    club: ClubCreate,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new club (admin only)"""
    # Check if club already exists
    existing_club = crud.get_club_by_name(db, club.name)
    if existing_club:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Club with this name already exists"
        )
    
    new_club = crud.create_club(db, club)
    return new_club


# Membership management
@router.post("/{club_id}/join", response_model=MembershipResponse)
def join_club(
    club_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request to join a club"""
    # Check if club exists
    club = crud.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    # Check if user is already a member
    existing_membership = crud.get_membership(db, current_user["user_id"], club_id)
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member or has a pending request"
        )
    
    # Create membership request
    membership = crud.create_membership(
        db,
        MembershipCreate(user_id=current_user["user_id"], club_id=club_id)
    )
    return membership


@router.delete("/{club_id}/leave")
def leave_club(
    club_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a club"""
    # Check if membership exists
    membership = crud.get_membership(db, current_user["user_id"], club_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this club"
        )
    
    crud.delete_membership(db, current_user["user_id"], club_id)
    return {"message": "Successfully left the club"}


@router.get("/{club_id}/members", response_model=list[dict])
def get_club_members(
    club_id: int,
    status: str = Query("approved"),
    db: Session = Depends(get_db)
):
    """Get members of a club"""
    club = crud.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    memberships = crud.get_club_members(db, club_id, status)
    
    members = []
    for membership in memberships:
        user = crud.get_user_by_id(db, membership.user_id)
        if user:
            members.append({
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "membership_status": membership.status
            })
    
    return members


@router.put("/{club_id}/members/{user_id}", response_model=MembershipResponse)
def approve_membership(
    club_id: int,
    user_id: int,
    update: MembershipUpdate,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject membership request (admin only)"""
    membership = crud.update_membership(db, user_id, club_id, update)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership request not found"
        )
    return membership


@router.get("/{club_id}/pending-requests", response_model=list[MembershipResponse])
def get_pending_requests(
    club_id: int,
    current_user: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending membership requests for a club"""
    club = crud.get_club_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    
    memberships = db.query(crud.Membership).filter(
        crud.Membership.club_id == club_id,
        crud.Membership.status == "pending"
    ).all()
    
    return memberships
