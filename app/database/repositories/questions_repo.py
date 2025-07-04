from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.database.models import Question, Tag


class QuestionsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, question_id: int) -> Question | None:
        return await self.session.get(Question, question_id)

    async def add(
        self, title: str, content: str, author_id: int, tags: list[str], anonymous: bool
    ) -> Question:
        question = Question(
            title=title,
            content=content,
            author_id=author_id,
            tags=tags,
            anonymous=anonymous,
        )
        self.session.add(question)
        await self.session.flush()
        return question

    async def get_n_current_questions_with_offset(
        self, limit: int, offset: int
    ) -> list[Question]:
        questions = await self.session.execute(
            select(Question)
            .limit(limit)
            .offset(offset)
            .order_by(Question.answers_id.desc())
        )
        questions = questions.scalars().all()
        return questions

    async def get_n_top_questions(self, limit: int) -> list[Question]:
        questions = await self.session.execute(
            select(Question)
            .order_by(func.char_length(Question.answers_id).desc())
            .limit(limit)
        )
        questions = questions.scalars().all()
        return questions

    async def get_all_questions(self) -> list[Question]:
        questions = await self.session.execute(select(Question))
        questions = questions.scalars().all()
        return questions

    async def get_questions_count(self) -> int:
        questions = await self.get_all_questions()
        return len(questions)
