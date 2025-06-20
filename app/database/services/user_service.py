from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository, session: AsyncSession):
        self.user_repo = user_repo
        self.session = session
    
    async def get_user(self, telegram_id: int) -> User | None:
        return await self.user_repo.get(telegram_id)
    
    async def add_user(self, telegram_id: int, username: str) -> None:
        user = await self.get_user(telegram_id)
        if user:
            return
        await self.user_repo.add(telegram_id, username)
        await self.session.commit()
    
    async def add_question_id(self, telegram_id: int, question_id: int) -> None:
        await self.user_repo.add_question_id(telegram_id, question_id)
        await self.session.commit()
    
    async def add_answer_id(self, user_id: int, answer_id: int) -> None:
        await self.user_repo.add_answer_id(user_id, answer_id)
        await self.session.commit()
    
    async def change_name(self, user_id: int, new_name: str) -> None:
        await self.user_repo.change_name(user_id, new_name)
        await self.session.commit()