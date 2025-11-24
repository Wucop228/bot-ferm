from uuid import uuid4

import pytest
from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import login_v1
from app.api.v1.users import create_user
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


def _make_user_create(login: str, password: str) -> UserCreate:
    return UserCreate(
        login=login,
        password=password,
        project_id=uuid4(),
        env="stage",
        domain="regular",
    )


@pytest.mark.asyncio
async def test_login_success(db_session: AsyncSession) -> None:
    login = f"user_{uuid4().hex}@example.com"
    password = "super-secret"
    user_in = _make_user_create(login, password)
    await create_user(user_in, db=db_session)

    payload = LoginRequest(login=login, password=password)
    response = Response()

    result = await login_v1(payload, response=response, db=db_session)

    assert result == {"detail": "Successful login v1"}
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "access_token=" in set_cookie


@pytest.mark.asyncio
async def test_login_wrong_password(db_session: AsyncSession) -> None:
    login = f"user_{uuid4().hex}@example.com"
    password = "super-secret"
    user_in = _make_user_create(login, password)
    await create_user(user_in, db=db_session)

    payload = LoginRequest(login=login, password="wrong-password")
    response = Response()

    with pytest.raises(HTTPException) as exc:
        await login_v1(payload, response=response, db=db_session)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(db_session: AsyncSession) -> None:
    payload = LoginRequest(
        login=f"unknown_{uuid4().hex}@example.com",
        password="whatever",
    )
    response = Response()

    with pytest.raises(HTTPException) as exc:
        await login_v1(payload, response=response, db=db_session)

    assert exc.value.status_code == 401