import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.questions_repo import QuestionsRepository
from app.database.repositories.answer_repo import AnswerRepository
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.tags_repo import TagsRepo
from app.database.models import Question


class QuestionsService:
    def __init__(
        self,
        questions_repo: QuestionsRepository,
        user_repo: UserRepository,
        answer_repo: AnswerRepository,
        tags_repo: TagsRepo,
        session: AsyncSession,
    ) -> None:
        self.questions_repo = questions_repo
        self.user_repo = user_repo
        self.answer_repo = answer_repo
        self.session = session
        self.tags_repo = tags_repo

    async def get_question(self, question_id: int) -> Question | None:
        return await self.questions_repo.get(question_id)

    async def add_question(
        self, title: str, content: str, author_id: int, tags: list[str], anonymous: bool
    ) -> Question:
        if not tags:
            tags = [""]
        else:
            for tag in tags:
                current_tag = await self.tags_repo.get_tag(tag)
                if not current_tag:
                    await self.tags_repo.add_tag(tag)
            await self.session.flush()

        question = await self.questions_repo.add(
            title, content, author_id, tags, anonymous
        )

        await self.tags_repo.add_question_id(tags, question.question_id)

        await self.session.commit()
        return question

    async def get_n_questions_without_answer_by_page(
        self, limit: int, page
    ) -> list[Question]:
        offset = (page - 1) * limit
        questions = (
            await self.questions_repo.get_n_questions_without_answer_with_offset(
                limit, offset
            )
        )
        return questions

    async def get_n_top_questions(self, limit: int) -> list[Question]:
        questions = await self.questions_repo.get_n_top_questions(limit)
        return questions

    async def answer_question(
        self, content: str, question_id: int, user_id: int, anonymous: bool
    ) -> None:
        try:
            answer = await self.answer_repo.add_answer(
                content, user_id, question_id, anonymous
            )
            await self.answer_repo.answer_question(question_id, answer.answer_id)
            await self.user_repo.add_answer_id(user_id, answer.answer_id)
            await self.session.commit()
        except Exception as e:
            logging.exception(e)
            await self.session.rollback()

    async def get_questions_count(self) -> int:
        return await self.questions_repo.get_questions_count()

    async def get_answers(self, question_id: int):
        return await self.answer_repo.get_answers(question_id)
