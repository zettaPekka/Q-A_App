from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.questions_repo import QuestionsRepository
from app.database.repositories.answer_repo import AnswerRepository
from app.database.repositories.user_repo import UserRepository


class QuestionsService:
    def __init__(self,
        questions_repo: QuestionsRepository,
        user_repo: UserRepository, 
        answer_repo: AnswerRepository,
        session: AsyncSession,
    ):
        self.questions_repo = questions_repo
        self.user_repo = user_repo
        self.answer_repo = answer_repo
        self.session = session

    async def get_question(self, question_id: int):
        return await self.questions_repo.get(question_id)

    async def add_question(self, title: str, content: str, author_id: int):
        question = await self.questions_repo.add(title, content, author_id)
        await self.session.commit()
        return question
    
    async def get_n_questions_without_answer(self, limit: int):
        questions = await self.questions_repo.get_n_questions_without_answer(limit)
        questions = [{'title':question.title, 'author_id':question.author_id, 'content':question.content} for question in questions]
        return questions

    async def get_n_questions(self, limit: int):
        return await self.questions_repo.get_n_questions(limit)
    
    async def answer_question(self, content: str, question_id: int, user_id: int):
        try:
            answer = await self.answer_repo.add_answer(content, user_id, question_id)
            await self.questions_repo.answer_question(question_id, answer.answer_id)
            await self.user_repo.add_answer_id(user_id, answer.answer_id)
            await self.session.commit()
            return answer
        except:
            await self.session.rollback()
            return None