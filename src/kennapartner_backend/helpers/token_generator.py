import jwt
import os
from dotenv import load_dotenv
import datetime
from datetime import timezone

load_dotenv()


def create_tokens(user_id: str):
    access_token = jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(days=30),
        },
        os.getenv("JWT_SECRET"),
        algorithm="HS256",
    )
    refresh_token = jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(days=60),
        },
        os.getenv("JWT_SECRET"),
        algorithm="HS256",
    )

    return (access_token, refresh_token)
