from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.services.user_dao import UserDAO
from app.core.database import get_db_session
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", response_model=list[UserRead])
async def get_users(db: AsyncSession = Depends(get_db_session)):
    dao = UserDAO(db)
    users = await dao.find_all()
    return users

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    dao = UserDAO(db)

    data = user_in.model_dump()
    data["password"] = get_password_hash(user_in.password)

    try:
        user = await dao.create(data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this login already exists",
        )

    return user

@router.post("/{user_id}/acquire-lock", response_model=UserRead)
async def acquire_lock(user_id: UUID, db: AsyncSession = Depends(get_db_session)):
    dao = UserDAO(db)

    user = await dao.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.locktime is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already locked",
        )

    locked_user = await dao.acquire_lock(user_id)
    if locked_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already locked",
        )

    return locked_user


@router.post("/{user_id}/release-lock", response_model=UserRead)
async def release_lock(user_id: UUID, db: AsyncSession = Depends(get_db_session)):
    dao = UserDAO(db)

    user = await dao.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    released_user = await dao.release_lock(user_id)
    if released_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return released_user