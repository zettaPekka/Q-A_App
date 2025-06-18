from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Answer


class AnswerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_answer(self, content: str, author_id: int, question_id: int):
        answer = Answer(content=content, author_id=author_id, question_id=question_id)
        self.session.add(answer)
        await self.session.flush()
        return answer