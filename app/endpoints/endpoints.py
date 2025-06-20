from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Response, Query, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import app.auth.jwt_processing as jwt_processing
from app.schemas.question_schema import QuestionSchema
from app.schemas.auth_schema import TelegramAuthData
from app.schemas.answer_schema import AnswerSchema
from app.auth.hashing import verify_telegram_hash
from app.database.services.user_service import UserService
from app.database.services.questions_service import QuestionsService
from app.database.services.tags_service import TagsService
from app.dependencies.dependencies import get_user_service, get_questions_service, get_current_user_id, get_tags_service


load_dotenv()

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/')
async def index(
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
):
    query_params = request.query_params
    try:
        page = int(query_params.get('page', 1))
        page = max(page, 1)
    except ValueError:
        page = 1
    
    questions = await question_service.get_n_questions_without_answer_by_page(8, page)
    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    if user_id:
        user = await user_service.get_user(user_id)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'user': user,
            'questions':questions,
            'top_questions': top_questions,
            'top_tags': top_tags,
            'questions_count': questions_count,
            'page':page
        })
    
    return templates.TemplateResponse('index.html', {
        'request': request,
        'user': None,
        'bot_username': os.getenv('BOT_USERNAME'),
        'questions':questions,
        'top_questions': top_questions,
        'top_tags': top_tags,
        'questions_count': questions_count,
        'page':page
    })


@router.get('/profile/{user_id}')
async def profile(
    user_id,
    request: Request,
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    questions_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    top_questions = await questions_service.get_n_top_questions(5)
    questions_count = await questions_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)
    user = await user_service.get_user(user_id)
    user_questions = await questions_service.get_public_questions(user_id) 
    user_answers = await questions_service.get_public_answers(user_id)
    
    if current_user_id:
        current_user = await user_service.get_user(current_user_id)
        response = templates.TemplateResponse('profile.html', {
            'request': request,
            'user': current_user,
            'profile_user': user,
            'user_questions': user_questions,
            'user_answers': user_answers,
            'top_questions': top_questions,
            'top_tags': top_tags,
            'questions_count': questions_count,
            'user_questions_count': len(user_questions),
            'answers_count': len(user_answers)
        })
        return response

    response = templates.TemplateResponse('profile.html', {
        'request': request,
        'user': None,
        'profile_user': user,
        'user_questions': user_questions,
        'user_answers': user_answers,
        'top_questions': top_questions,
        'top_tags': top_tags,
        'questions_count': questions_count,
        'user_questions_count': len(user_questions),
        'answers_count': len(user_answers)
    })
    return response


@router.get('/ask/')
async def ask(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service)
):
    if not user_id:
        return RedirectResponse('/') #TODO: redirect to login page

    user = await user_service.get_user(user_id)
    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)
    
    response = templates.TemplateResponse('ask.html', {
        'request': request,
        'user': user,
        'top_questions': top_questions,
        'top_tags': top_tags,
        'questions_count': questions_count,
    })
    return response


@router.get('/question/{question_id}/')
async def question(
    question_id,
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    tags_service: TagsService = Depends(get_tags_service),
    user_id: int = Depends(get_current_user_id),
):
    question = await question_service.get_question(question_id)
    top_questions = await question_service.get_n_top_questions(3)
    top_tags = await tags_service.get_n_top_tags(7)
    answers = await question_service.get_answers(question_id)
    questions_count = await question_service.get_questions_count()
    user = await user_service.get_user(user_id)
    
    if not question:
        response = templates.TemplateResponse('page404.html', {
            'request': request,
            'user':user
        })
        return response
    
    if user_id:
        response = templates.TemplateResponse('question.html', {
            'request': request,
            'user': user,
            'question': question,
            'top_questions': top_questions,
            'top_tags': top_tags,
            'answers': answers,
            'questions_count': questions_count,
            'answers_count': len(answers)
        })
        return response
    
    response = templates.TemplateResponse('question.html', {
        'request': request,
        'user_id': None,
        'question': question,
        'top_questions':top_questions,
        'top_tags': top_tags,
        'answers': answers,
        'questions_count': questions_count,
        'answers_count': len(answers)
    })
    return response


@router.post('/question/')
async def question(
    request: Request,
    question: QuestionSchema = Form(),
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id) 
):
    if not user_id:
        return Response(status_code=401)
    
    added_question = await question_service.add_question(question.title, question.content, user_id, question.tags, question.anonymous) # TODO add anonymous field
    await user_service.add_question_id(user_id, added_question.question_id)
    
    return RedirectResponse(f'/question/{added_question.question_id}/', status_code=303)


@router.post('/question/{question_id}/answer')
async def answer_question(
    question_id: int,
    answer_data: AnswerSchema = Form(),
    question_service: QuestionsService = Depends(get_questions_service),
    user_id: int = Depends(get_current_user_id) 
):
    if not user_id:
        return Response(status_code=401)

    await question_service.answer_question(answer_data.content, question_id, user_id, answer_data.anonymous)
    
    response = RedirectResponse(f'/question/{question_id}/', status_code=303)
    return response


@router.post('/change/name/')
async def change_name(
    request: Request,
    new_name: str = Form(max_length=20),
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    if not user_id:
        return Response(status_code=401)
    
    await user_service.change_name(user_id, new_name)
    return RedirectResponse(f'/profile/{user_id}/', status_code=303)


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
    response = RedirectResponse('/')
    response.set_cookie(
        key=jwt_processing.config.JWT_ACCESS_COOKIE_NAME,
        value=jwt_processing.create_access_jwt(user_id='723444345429732'),
        expires=datetime.now(timezone.utc) + timedelta(days=100), 
        httponly=True,
        secure=False,
        samesite='lax'
    )
    await user_service.add_user('723444345429732', 'sdf')
    return response


@router.get('/logout/')
async def logout():
    response = RedirectResponse('/')
    response.delete_cookie(jwt_processing.config.JWT_ACCESS_COOKIE_NAME)
    return response