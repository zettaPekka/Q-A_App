from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Response, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import app.auth.jwt_processing as jwt_processing
from app.schemas.question_schema import QuestionSchema
from app.schemas.auth_schema import TelegramAuthData
from app.schemas.answer_schema import AnswerSchema
from app.auth.hashing import verify_telegram_hash
from app.database.services.user_service import UserService
from app.database.services.questions_service import QuestionsService
from app.dependencies.dependencies import get_user_service, get_questions_service, get_current_user_id


load_dotenv()

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/')
async def index(
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id) 
):
    questions = await question_service.get_n_questions_without_answer(10)

    if user_id:
        user = await user_service.get_user(user_id)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'user': user,
            'questions':questions
        })
    
    return templates.TemplateResponse('index.html', {
        'request': request,
        'user': None,
        'bot_username': os.getenv('BOT_USERNAME'),
        'questions':questions
    })


@router.get('/profile/')
async def profile(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    if user_id:
        user = await user_service.get_user(user_id)
        response = templates.TemplateResponse('profile.html', {
            'request': request,
            'user': user
        })
        return response
    
    response = templates.TemplateResponse('profile.html', {
        'request': request,
        'user': None
    })
    return response


@router.get('/question/{question_id}/')
async def question(
    question_id: int,
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id)
):
    question = await question_service.get_question(question_id)
    
    if not question:
        response = templates.TemplateResponse('page404.html', {
            'request': request
        })
        return response
    
    if user_id:
        user = await user_service.get_user(user_id)
        response = templates.TemplateResponse('question.html', {
            'request': request,
            'user': user,
            'question': question
        })
        return response
    
    response = templates.TemplateResponse('question.html', {
        'request': request,
        'user_id': None,
        'question': question
    })
    return response


@router.post('/question/')
async def question(
    question: QuestionSchema,
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id) 
):
    
    if not user_id:
        return Response(status_code=401)

    added_question = await question_service.add_question(question.title, question.content, user_id)
    await user_service.add_question_id(user_id, added_question.question_id)
    
    return added_question


@router.post('/question/{question_id}/answer')
async def answer_question(
    question_id: int,
    answer_data: AnswerSchema,
    question_service: QuestionsService = Depends(get_questions_service),
    user_id: int = Depends(get_current_user_id) 
):
    if not user_id:
        return Response(status_code=401)
    
    answer = await question_service.answer_question(answer_data.content, question_id, user_id)
    
    return answer


@router.get('/auth/telegram/')
async def auth_telegram(
    telegram_data: TelegramAuthData = Query(),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id) 
):
    if user_id:
        return Response(status_code=400) 
    
    is_valid = verify_telegram_hash(received_data=telegram_data.model_dump())
    if not is_valid:
        return Response(status_code=400)
    
    await user_service.add_user(telegram_data.id, telegram_data.first_name)
    
    response = RedirectResponse('/')
    response.set_cookie(
            key=jwt_processing.config.JWT_ACCESS_COOKIE_NAME,
            value=jwt_processing.create_access_jwt(user_id=str(telegram_data.id)),
            expires=datetime.now(timezone.utc) + timedelta(days=30), 
            httponly=True,
            secure=False, # TODO: change to True in production
            samesite='lax'
        )
    return response



'''TEST'''



@router.get('/login/')
async def login(
    user_service: UserService = Depends(get_user_service)
):
    response = Response(status_code=200)
    response.set_cookie(
        key=jwt_processing.config.JWT_ACCESS_COOKIE_NAME,
        value=jwt_processing.create_access_jwt(user_id='7354297309'),
        expires=datetime.now(timezone.utc) + timedelta(days=100), 
        httponly=True,
        secure=False,
        samesite='lax'
    )
    await user_service.add_user('7354297309', 'олег')
    return response


@router.get('/logout/')
async def logout():
    response = Response(status_code=200)
    response.delete_cookie(jwt_processing.config.JWT_ACCESS_COOKIE_NAME)
    return response