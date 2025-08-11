from dotenv import load_dotenv
from fastapi import APIRouter, Response, Depends, Form, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.schemas.question_schema import QuestionSchema
from app.schemas.answer_schema import AnswerSchema
from app.schemas.like_schema import LikeSchema
from app.database.services.user_service import UserService
from app.database.services.answer_service import AnswerService
from app.database.services.questions_service import QuestionsService
from app.dependencies.dependencies import (
    get_user_service,
    get_questions_service,
    get_current_user_id,
    get_answer_service,
)


load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/question/")
async def question(
    question: QuestionSchema = Form(),
    question_service: QuestionsService = Depends(get_questions_service),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
):
    if not user_id:
        return Response(status_code=401)

    added_question = await question_service.add_question(
        question.title, question.content, user_id, question.tags, question.anonymous
    )
    await user_service.add_question_id(user_id, added_question.question_id)

    return RedirectResponse(f"/question/{added_question.question_id}/", status_code=303)


@router.post("/question/{question_id}/answer")
async def answer_question(
    question_id: int,
    answer_data: AnswerSchema = Form(),
    question_service: QuestionsService = Depends(get_questions_service),
    user_id: int = Depends(get_current_user_id),
):
    if not user_id:
        return Response(status_code=401)

    response = RedirectResponse(f"/question/{question_id}/", status_code=303)

    if answer_data.content.strip() == "":
        return response

    await question_service.answer_question(
        answer_data.content, question_id, user_id, answer_data.anonymous
    )

    return response


@router.post("/change/name/")
async def change_name(
    new_name: str = Form(max_length=20),
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    if not user_id:
        return Response(status_code=401)

    await user_service.change_name(user_id, new_name)
    return RedirectResponse(f"/profile/{user_id}/", status_code=303)


@router.post("/answer/like/")
async def like_question(
    like_data: LikeSchema = Body(),
    user_id: int = Depends(get_current_user_id),
    answer_service: AnswerService = Depends(get_answer_service),
):
    if not user_id:
        return Response(status_code=401)

    action = await answer_service.action_answer(like_data.answer_id, user_id)
    return action
