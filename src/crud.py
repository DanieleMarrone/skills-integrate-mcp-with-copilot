"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from models import User, Club, Membership, RoleEnum
from security import hash_password, verify_password
from schemas import UserRegister, UserUpdate, ClubCreate, MembershipCreate, MembershipUpdate


# User CRUD operations
def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserRegister, role: str = "student") -> User:
    """Create a new user"""
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=RoleEnum(role),
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """Update user information"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Authenticate user by username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Club CRUD operations
def get_club_by_id(db: Session, club_id: int) -> Club:
    """Get club by ID"""
    return db.query(Club).filter(Club.id == club_id).first()


def get_club_by_name(db: Session, name: str) -> Club:
    """Get club by name"""
    return db.query(Club).filter(Club.name == name).first()


def get_all_clubs(db: Session) -> list:
    """Get all clubs"""
    return db.query(Club).all()


def create_club(db: Session, club: ClubCreate) -> Club:
    """Create a new club"""
    db_club = Club(**club.dict())
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


# Membership CRUD operations
def create_membership(db: Session, membership: MembershipCreate) -> Membership:
    """Create a new membership"""
    db_membership = Membership(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership


def get_membership(db: Session, user_id: int, club_id: int) -> Membership:
    """Get membership for a user and club"""
    return db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.club_id == club_id
    ).first()


def get_user_memberships(db: Session, user_id: int) -> list:
    """Get all memberships for a user"""
    return db.query(Membership).filter(Membership.user_id == user_id).all()


def get_club_members(db: Session, club_id: int, status: str = "approved") -> list:
    """Get members of a club"""
    return db.query(Membership).filter(
        Membership.club_id == club_id,
        Membership.status == status
    ).all()


def update_membership(
    db: Session,
    user_id: int,
    club_id: int,
    status_update: MembershipUpdate
) -> Membership:
    """Update membership status"""
    membership = get_membership(db, user_id, club_id)
    if not membership:
        return None
    
    membership.status = status_update.status
    db.commit()
    db.refresh(membership)
    return membership


def delete_membership(db: Session, user_id: int, club_id: int) -> bool:
    """Delete a membership"""
    membership = get_membership(db, user_id, club_id)
    if not membership:
        return False
    
    db.delete(membership)
    db.commit()
    return True
