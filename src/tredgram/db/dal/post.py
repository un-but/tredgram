"""Модуль для работы с постами в базе данных."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.base import ExecutableOption
from tredgram.db.models import PostModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from tredgram.schemas import PostCreate, PostUpdate


class PostDAL:
    """Класс для работы с постами в базе данных."""

    _default_opts: tuple[ExecutableOption, ...] = (joinedload(PostModel.user),)

    @staticmethod
    async def create(user_id: uuid.UUID, post_info: PostCreate, session: AsyncSession) -> PostModel:
        post = PostModel(user_id=user_id, **post_info.model_dump())

        session.add(post)
        await session.commit()

        return await PostDAL.get_by_id(post.id, session)

    @staticmethod
    async def get_by_id(
        post_id: int,
        session: AsyncSession,
    ) -> PostModel:
        if post := await session.scalar(
            select(PostModel).where(PostModel.id == post_id).options(*PostDAL._default_opts)
        ):
            return post

        msg = "Указанный пост не найден"
        raise LookupError(msg)

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[PostModel]:
        posts = await session.scalars(select(PostModel).options(*PostDAL._default_opts))
        return posts.unique().all()

    @staticmethod
    async def update(
        post_id: int,
        update_info: PostUpdate,
        session: AsyncSession,
    ) -> PostModel:
        post = await PostDAL.get_by_id(post_id, session)

        for field, value in update_info.model_dump(exclude_none=True).items():
            setattr(post, field, value)

        await session.commit()
        return await PostDAL.get_by_id(post.id, session)

    @staticmethod
    async def drop(post_id: uuid.UUID, session: AsyncSession) -> None:
        post = await PostDAL.get_by_id(post_id, session)

        await session.delete(post)
        await session.commit()
