import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.questions_repo import QuestionsRepository
from app.database.repositories.answer_repo import AnswerRepository
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.tags_repo import TagsRepo
from app.database.models import Question


class AnswerService:
    def __init__(
        self,
        answer_repo: AnswerRepository,
        session: AsyncSession,
    ) -> None:
        self.answer_repo = answer_repo
        self.session = session

    async def action_answer(self, answer_id: int, user_id: int):
        answer = await self.answer_repo.get_answer(answer_id)
        if user_id in answer.likes:
            await self.answer_repo.unlike_answer(answer_id, user_id)
            print("unlike")
            return {"action": "unliked"}
        else:
            await self.answer_repo.like_answer(answer_id, user_id)
            print("like")
            return {"action": "liked"}
