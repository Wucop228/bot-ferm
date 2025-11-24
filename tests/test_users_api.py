from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.users import create_user, get_users, acquire_lock, release_lock
from app.schemas.user import UserCreate
from app.services.user_dao import UserDAO


def _make_user_create(login: str | None = None) -> UserCreate:
    if login is None:
        login = f"user_{uuid4().hex}@example.com"
    return UserCreate(
        login=login,
        password="secret-password",
        project_id=uuid4(),
        env="stage",
        domain="regular",
    )


@pytest.mark.asyncio
async def test_create_user_success(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    assert created.id is not None
    assert created.login == user_in.login
    assert created.locktime is None
    assert created.password != user_in.password  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_create_user_conflict_login(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    await create_user(user_in, db=db_session)

    with pytest.raises(HTTPException) as exc:
        await create_user(user_in, db=db_session)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc.value.detail


@pytest.mark.asyncio
async def test_get_users_returns_created_user(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    users = await get_users(db=db_session)
    logins = [u.login for u in users]

    assert created.login in logins


@pytest.mark.asyncio
async def test_acquire_lock_success(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    locked = await acquire_lock(created.id, db=db_session)

    assert locked.locktime is not None


@pytest.mark.asyncio
async def test_acquire_lock_user_not_found(db_session: AsyncSession) -> None:
    fake_id = uuid4()

    with pytest.raises(HTTPException) as exc:
        await acquire_lock(fake_id, db=db_session)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_acquire_lock_user_already_locked(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    await acquire_lock(created.id, db=db_session)

    with pytest.raises(HTTPException) as exc:
        await acquire_lock(created.id, db=db_session)

    assert exc.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_acquire_lock_returns_none_raises_409(db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    async def fake_acquire_lock(self, user_id):  # type: ignore[override]
        return None

    monkeypatch.setattr(UserDAO, "acquire_lock", fake_acquire_lock)

    with pytest.raises(HTTPException) as exc:
        await acquire_lock(created.id, db=db_session)

    assert exc.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_release_lock_success(db_session: AsyncSession) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    await acquire_lock(created.id, db=db_session)
    released = await release_lock(created.id, db=db_session)

    assert released.locktime is None


@pytest.mark.asyncio
async def test_release_lock_user_not_found(db_session: AsyncSession) -> None:
    fake_id = uuid4()

    with pytest.raises(HTTPException) as exc:
        await release_lock(fake_id, db=db_session)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_release_lock_returns_none_raises_404(db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    user_in = _make_user_create()
    created = await create_user(user_in, db=db_session)

    async def fake_release_lock(self, user_id):  # type: ignore[override]
        return None

    monkeypatch.setattr(UserDAO, "release_lock", fake_release_lock)

    with pytest.raises(HTTPException) as exc:
        await release_lock(created.id, db=db_session)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND