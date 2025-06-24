from pydantic import BaseModel


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str
