from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Response, Query, Depends, Form, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import app.auth.jwt_processing as jwt_processing
from app.schemas.question_schema import QuestionSchema
from app.schemas.auth_schema import TelegramAuthData
from app.schemas.answer_schema import AnswerSchema
from app.schemas.like_schema import LikeSchema
from app.auth.hashing import verify_telegram_hash
from app.database.services.user_service import UserService
from app.database.services.answer_service import AnswerService
from app.database.services.questions_service import QuestionsService
from app.database.services.tags_service import TagsService
from app.dependencies.dependencies import (
    get_user_service,
    get_questions_service,
    get_current_user_id,
    get_tags_service,
    get_answer_service,
)


load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
bot_username = os.getenv("BOT_USERNAME")


@router.get("/")
async def index(
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int | None = Depends(get_current_user_id),
):
    query_params = request.query_params
    try:
        page = int(query_params.get("page", 1))
        page = max(page, 1)
    except ValueError:
        page = 1

    questions = await question_service.get_n_current_questions_by_page(8, page)

    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    user = await user_service.get_user(user_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "questions": questions,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "page": page,
            "bot_username": bot_username,
        },
    )


@router.get("/profile/{user_id}/")
async def profile(
    user_id,
    request: Request,
    current_user_id: int | None = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    questions_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    top_questions = await questions_service.get_n_top_questions(5)
    questions_count = await questions_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    user = await user_service.get_user(user_id)

    current_user = await user_service.get_user(current_user_id)

    is_private = user_id.isdigit() and int(user_id) == current_user_id
    user_questions = await user_service.get_user_questions(user_id, is_private)
    user_answers = await user_service.get_user_answers(user_id, is_private)

    response = templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user,
            "profile_user": user,
            "user_questions": user_questions,
            "user_answers": user_answers,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "user_questions_count": len(user_questions),
            "answers_count": len(user_answers),
            "bot_username": bot_username,
        },
    )

    return response


@router.get("/ask/")
async def ask(
    request: Request,
    user_id: int | None = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    if not user_id:
        return RedirectResponse("/")  # TODO: redirect to login page

    user = await user_service.get_user(user_id)

    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    response = templates.TemplateResponse(
        "ask.html",
        {
            "request": request,
            "user": user,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "bot_username": bot_username,
        },
    )
    return response


@router.get("/question/{question_id}/")
async def question(
    question_id,
    request: Request,
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    tags_service: TagsService = Depends(get_tags_service),
    user_id: int | None = Depends(get_current_user_id),
):
    question = await question_service.get_question(question_id)

    top_questions = await question_service.get_n_top_questions(2)
    top_tags = await tags_service.get_n_top_tags(7)
    questions_count = await question_service.get_questions_count()

    answers = await question_service.get_answers(question_id)
    user = await user_service.get_user(user_id)

    if not question:
        response = templates.TemplateResponse(
            "page404.html", {"request": request, "user": user}
        )
        return response

    response = templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "user": user,
            "question": question,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "answers": answers,
            "questions_count": questions_count,
            "answers_count": len(answers),
            "bot_username": bot_username,
        },
    )
    return response


@router.get("/rules/")
async def rules(
    request: Request,
    user_id: int | None = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    user = await user_service.get_user(user_id)

    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    response = templates.TemplateResponse(
        "rules.html",
        {
            "request": request,
            "user": user,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "bot_username": bot_username,
        },
    )
    return response


@router.get("/about/")
async def rules(
    request: Request,
    user_id: int | None = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    user = await user_service.get_user(user_id)

    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)
    
    users_count = len(await user_service.get_all_users())
    tags_count = len(await tags_service.get_all_tags())

    response = templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": user,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "bot_username": bot_username,
            'users_count':users_count,
            'tags_count':tags_count
        },
    )
    return response


@router.get('/tag/{tag_name}/')
async def questions_by_tag(
    request: Request,
    tag_name: str,
    user_id: int | None = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    question_service: QuestionsService = Depends(get_questions_service),
    tags_service: TagsService = Depends(get_tags_service),
):
    query_params = request.query_params
    try:
        page = int(query_params.get("page", 1))
        page = max(page, 1)
    except ValueError:
        page = 1

    questions = await question_service.get_n_questions_by_tag_by_page(8, tag_name, page)

    top_questions = await question_service.get_n_top_questions(5)
    questions_count = await question_service.get_questions_count()
    top_tags = await tags_service.get_n_top_tags(7)

    user = await user_service.get_user(user_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "questions": questions,
            "top_questions": top_questions,
            "top_tags": top_tags,
            "questions_count": questions_count,
            "page": page,
            "bot_username": bot_username,
            'tag_filter': True,
            'tag_name':tag_name
        },
    )


@router.get("/{path:path}/")
async def not_found(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    user_id: int | None = Depends(get_current_user_id),
):
    user = await user_service.get_user(user_id)
    response = templates.TemplateResponse(
        "page404.html", {"request": request, "user": user}
    )
    return response