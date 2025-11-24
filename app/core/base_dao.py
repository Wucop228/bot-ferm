from uuid import UUID

from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, id_: UUID):
        stmt = select(self.model).where(self.model.id == id_)  # type: ignore[attr-defined]
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, obj_in):
        obj = self.model(**obj_in)  # type: ignore[call-arg]
        self.session.add(obj)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise
        await self.session.refresh(obj)
        return obj

    async def update( self, id_: UUID, values):
        stmt = (
            sqlalchemy_update(self.model)  # type: ignore[arg-type]
            .where(self.model.id == id_)  # type: ignore[attr-defined]
            .values(**values)
            .returning(self.model)  # type: ignore[arg-type]
        )
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise
        return obj

    async def delete(self, id_: UUID):
        stmt = sqlalchemy_delete(self.model).where(self.model.id == id_)  # type: ignore[arg-type]
        await self.session.execute(stmt)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise