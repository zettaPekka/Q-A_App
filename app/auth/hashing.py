from hashlib import sha256
import os
import hmac

from dotenv import load_dotenv


load_dotenv()


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def verify_telegram_hash(received_data: dict) -> bool:
    received_hash = received_data.pop('hash')

    data_check_string = '\n'.join(
        f'{key}={value}' 
        for key, value in sorted(received_data.items())
    )

    secret_key = sha256(os.getenv('BOT_TOKEN').encode()).digest()

    expected_hash = hmac.new(
        secret_key, 
        data_check_string.encode(), 
        sha256
    ).hexdigest()

    return hmac.compare_digest(expected_hash, received_hash)