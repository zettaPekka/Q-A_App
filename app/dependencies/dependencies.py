from fastapi import Depends, Request

from app.database.repositories.user_repo import UserRepository
from app.database.services.user_service import UserService
from app.database.init_database import session_factory
from app.database.repositories.questions_repo import QuestionsRepository
from app.database.services.questions_service import QuestionsService
from app.database.repositories.answer_repo import AnswerRepository
from app.database.services.tags_service import TagsService
from app.database.repositories.tags_repo import TagsRepo
import app.auth.jwt_processing as jwt_processing


async def get_db_session():
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_user_service(session=Depends(get_db_session)):
    user_repo = UserRepository(session)
    return UserService(user_repo, session)


def get_tags_service(session=Depends(get_db_session)):
    tags_repo = TagsRepo(session)
    return TagsService(tags_repo, session)


def get_questions_service(session=Depends(get_db_session)):
    questions_repo = QuestionsRepository(session)
    user_repo = UserRepository(session)
    answer_repo = AnswerRepository(session)
    tags_repo = TagsRepo(session)
    return QuestionsService(questions_repo, user_repo, answer_repo, tags_repo, session)


async def get_current_user_id(request: Request):
    jwt_cookie = request.cookies.get(jwt_processing.config.JWT_ACCESS_COOKIE_NAME)
    if jwt_cookie and (jwt_payload := jwt_processing.decode_access_jwt(jwt_cookie)):
        return int(jwt_payload.get("sub"))
    return None
