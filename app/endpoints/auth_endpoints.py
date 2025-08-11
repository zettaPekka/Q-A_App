from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Response, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import app.auth.jwt_processing as jwt_processing
from app.schemas.auth_schema import TelegramAuthData
from app.auth.hashing import verify_telegram_hash
from app.database.services.user_service import UserService
from app.dependencies.dependencies import get_user_service, get_current_user_id


load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/auth/telegram/")
async def auth_telegram(
    telegram_data: TelegramAuthData = Query(),
    user_service: UserService = Depends(get_user_service),
    user_id: int = Depends(get_current_user_id),
):
    if user_id:
        return Response(status_code=400)

    is_valid = verify_telegram_hash(received_data=telegram_data.model_dump())
    if not is_valid:
        return Response(status_code=400)

    await user_service.add_user(telegram_data.id, telegram_data.first_name)

    response = RedirectResponse("/")
    response.set_cookie(
        key=jwt_processing.config.JWT_ACCESS_COOKIE_NAME,
        value=jwt_processing.create_access_jwt(user_id=str(telegram_data.id)),
        expires=datetime.now(timezone.utc) + timedelta(days=30),
        httponly=True,
        secure=False,  # TODO: change to True in production
        samesite="lax",
    )
    return response


@router.get("/logout/")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie(jwt_processing.config.JWT_ACCESS_COOKIE_NAME)
    return response


"""TEST"""
import random


@router.get("/login/")
async def login(user_service: UserService = Depends(get_user_service)):
    uid = str(random.randint(1, 100000))
    response = RedirectResponse("/")
    response.set_cookie(
        key=jwt_processing.config.JWT_ACCESS_COOKIE_NAME,
        value=jwt_processing.create_access_jwt(user_id=uid),
        expires=datetime.now(timezone.utc) + timedelta(days=100),
        httponly=True,
        secure=False,
        samesite="lax",
    )
    await user_service.add_user(uid, f"user_{uid[:4]}")
    return response
