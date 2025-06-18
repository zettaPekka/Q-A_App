from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get(self, telegram_id: int) -> User | None:
        return await self.session.get(User, telegram_id)
    
    async def add(self, telegram_id: int, username: str) -> None:
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
    
    async def add_question_id(self, telegram_id: int, question_id: int) -> None:
        user = await self.get(telegram_id)
        user.questions_id.append(question_id)
        flag_modified(user, 'questions_id')
    
    async def add_answer_id(self, user_id: int, answer_id: int) -> None:
        user = await self.get(user_id)
        user.answers_id.append(answer_id)
        flag_modified(user, 'answers_id')