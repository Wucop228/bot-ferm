from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.services.user_dao import UserDAO


@pytest.mark.asyncio
async def test_base_dao_crud(db_session: AsyncSession) -> None:
    dao = UserDAO(db_session)

    login = f"user_{uuid4().hex}@example.com"
    user_dict = {
        "login": login,
        "password": get_password_hash("secret"),
        "project_id": uuid4(),
        "env": "stage",
        "domain": "regular",
    }

    created = await dao.create(user_dict)
    assert created.id is not None
    assert created.login == login

    all_users = await dao.find_all()
    assert any(u.id == created.id for u in all_users)

    found = await dao.find_one(login=login)
    assert found is not None
    assert found.id == created.id

    by_id = await dao.get_by_id(created.id)
    assert by_id is not None
    assert by_id.login == login

    updated = await dao.update(created.id, {"env": "prod"})
    assert updated is not None
    assert updated.env == "prod"

    await dao.delete(created.id)
    deleted = await dao.get_by_id(created.id)
    assert deleted is None