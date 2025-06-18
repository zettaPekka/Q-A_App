from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.database.models import Question


class QuestionsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get(self, question_id: int) -> Question | None:
        return await self.session.get(Question, question_id) 
    
    async def add(self, title: str, content: str, author_id: int) -> Question:
        question = Question(title=title, content=content, author_id=author_id)
        self.session.add(question)
        await self.session.flush()
        return question
    
    async def get_n_questions_without_answer(self, limit: int) -> list[Question]:
        questions = await self.session.execute(select(Question).where(Question.without_answer == True).limit(limit))
        questions = questions.scalars().all()
        return questions
    
    async def get_n_questions(self, limit: int) -> list[Question]:
        questions = await self.session.execute(select(Question).limit(limit))
        questions = questions.scalars().all()
        return questions
    
    async def get_all_questions(self) -> list[Question]:
        questions = await self.session.execute(select(Question))
        questions = questions.scalars().all()
        return questions
    
    async def answer_question(self, question_id: int, answer_id: int) -> None:
        question = await self.get(question_id)
        question.answers_id.append(answer_id)
        flag_modified(question, 'answers_id')