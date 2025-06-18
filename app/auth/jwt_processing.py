import os
from datetime import timedelta

from authx import AuthX, AuthXConfig
from dotenv import load_dotenv
import jwt


load_dotenv()

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ALGORITHM = 'HS256'
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

security = AuthX(config)


def create_access_jwt(user_id: str) -> str:
    return security.create_access_token(uid=user_id)

def decode_access_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except:
        return None