from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Answer


class AnswerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def add_answer(self, content: str, author_id: int, question_id: int, anonymous: bool) -> Answer:
        answer = Answer(content=content, author_id=author_id, question_id=question_id, anonymous=anonymous)
        self.session.add(answer)
        await self.session.flush()
        return answer