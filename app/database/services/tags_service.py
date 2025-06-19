from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Tag
from app.database.repositories.tags_repo import TagsRepo


class TagsService:
    def __init__(self, tags_repo: TagsRepo, session: AsyncSession):
        self.tags_repo = tags_repo
        self.session = session

    async def get_tag(self, tag_name: str) -> Tag | None:
        return await self.tags_repo.get_tag(tag_name)
    
    async def get_n_top_tags(self, n: int) -> list[Tag]:
        return await self.tags_repo.get_n_top_tags(n)

    async def add_tag(self, tag_name: str) -> None:
        tag = await self.tags_repo.get_tag(tag_name)
        if not tag:
            await self.tags_repo.add_tag(tag_name)
        await self.session.commit()