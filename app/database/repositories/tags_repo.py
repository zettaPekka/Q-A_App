from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.database.models import Tag


class TagsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tag(self, tag_name: str) -> Tag | None:
        return await self.session.get(Tag, tag_name)

    async def get_n_top_tags(self, n: int) -> list[Tag]:
        tags = await self.session.execute(
            select(Tag).order_by(Tag.questions_id.desc()).limit(n)
        )
        tags = tags.scalars().all()
        return tags

    async def add_tag(self, tag_name: str) -> None:
        tag = Tag(tag_name=tag_name)
        self.session.add(tag)

    async def add_question_id(self, tags: list[str] | None, question_id: int) -> None:
        if tags != [""]:
            for tag in tags:
                tag = await self.get_tag(tag)
                tag.questions_id.append(question_id)
                flag_modified(tag, "questions_id")
    
    async def get_all_tags(self):
        tags = await self.session.execute(select(Tag))
        tags = tags.scalars().all()
        return tags
