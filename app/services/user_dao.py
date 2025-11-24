from sqlalchemy import update as sqlalchemy_update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_dao import BaseDAO
from app.models.user import User


class UserDAO(BaseDAO):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def acquire_lock(self, user_id):
        stmt = (
            sqlalchemy_update(User)
            .where(User.id == user_id, User.locktime.is_(None))
            .values(locktime=func.now())
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        await self.session.commit()
        return user

    async def release_lock(self, user_id):
        stmt = (
            sqlalchemy_update(User)
            .where(User.id == user_id)
            .values(locktime=None)
            .returning(User)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        await self.session.commit()
        return user
