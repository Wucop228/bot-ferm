from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import verify_password, create_jwt_token
from app.schemas.auth import LoginRequest
from app.services.user_dao import UserDAO

router = APIRouter(prefix="/api/v1/auth", tags=["auth-v1"])


@router.post("/login")
async def login_v1(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db_session)):
    dao = UserDAO(db)
    user = await dao.find_one(login=payload.login)

    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_jwt_token(
        data={"sub": str(user.id), "ver": "v1"},
        expires_delta=access_token_expires,
        token_type="access",
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=int(access_token_expires.total_seconds()),
    )

    return {"detail": "Successful login v1"}