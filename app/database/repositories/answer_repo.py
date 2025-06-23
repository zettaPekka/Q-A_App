from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.database.models import Answer, Question


class AnswerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def add_answer(self, content: str, author_id: int, question_id: int, anonymous: bool) -> Answer:
        answer = Answer(content=content, author_id=author_id, question_id=question_id, anonymous=anonymous)
        self.session.add(answer)
        await self.session.flush()
        return answer
    
    async def answer_question(self, question_id: int, answer_id: int) -> None:
        question = await self.session.get(Question, question_id)
        question.answers_id.append(answer_id)
        flag_modified(question, 'answers_id')

    async def get_answers(self, question_id: int) -> list[Answer]:
        answers = await self.session.execute(select(Answer).where(Answer.question_id == question_id))
        answers = answers.scalars().all()
        return answers
