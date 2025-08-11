from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Body
from app.database.services.questions_service import QuestionsService
from app.dependencies.dependencies import get_questions_service


load_dotenv()

router = APIRouter()


@router.post("/search/question/")
async def search_question(
    text: str = Body(embed=True),
    question_service: QuestionsService = Depends(get_questions_service),
):
    questions = await question_service.get_questions_by_search(text)
    return questions
