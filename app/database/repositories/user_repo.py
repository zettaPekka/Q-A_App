from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select, and_

from app.database.models import User, Question, Answer


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
        flag_modified(user, "questions_id")

    async def add_answer_id(self, user_id: int, answer_id: int) -> None:
        user = await self.get(user_id)
        user.answers_id.append(answer_id)
        flag_modified(user, "answers_id")

    async def change_name(self, user_id: int, new_name: str) -> None:
        user = await self.get(user_id)
        user.username = new_name

    async def get_user_questions(self, user_id: int):
        questions = await self.session.execute(
            select(Question).where(Question.author_id == user_id)
        )
        questions = questions.scalars().all()
        return questions

    async def get_user_answers(self, user_id: int):
        answers = await self.session.execute(
            select(Answer).where(Answer.author_id == user_id)
        )
        answers = answers.scalars().all()
        return answers

    async def get_public_user_questions(self, user_id: int):
        questions = await self.session.execute(
            select(Question).where(
                and_(Question.author_id == user_id, Question.anonymous != True)
            )
        )
        questions = questions.scalars().all()
        return questions

    async def get_public_user_answers(self, user_id: int):
        answers = await self.session.execute(
            select(Answer).where(
                and_(Answer.author_id == user_id, Answer.anonymous != True)
            )
        )
        answers = answers.scalars().all()
        return answers

    async def get_all_users(self):
        users = await self.session.execute(select(User))
        users = users.scalars().all()
        return users
