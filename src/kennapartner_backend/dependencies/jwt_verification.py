import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from fastapi import Depends, HTTPException
from ..utils import connect_to_database, logger
from ..modules import User
import os
from dotenv import load_dotenv

load_dotenv()
from motor.motor_asyncio import AsyncIOMotorClient


"""
Retrieve the current user based on the provided JWT token.

This asynchronous function decodes the JWT token to extract the user
identifier and fetches the corresponding user from the database. It
raises an HTTPException if the token is missing, invalid, expired, or
if no user is found.

Parameters:
    token (Annotated[HTTPAuthorizationCredentials]): The JWT token
        extracted from the request header.
    init_database (Annotated[AsyncIOMotorClient]): The initialized
        database client.

Returns:
    User: The user object associated with the token.

Raises:
    HTTPException: If the token is missing, invalid, expired, or if
        the user does not exist.
"""

security = HTTPBearer()


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
):
    if token.credentials is None:
        raise HTTPException(
            status_code=400,
            detail={"message": "Acess token required!"},
        )

    try:
        payload = jwt.decode(token.credentials, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user = await User.get(payload.get("sub"))
        if user is None:
            raise HTTPException(
                detail={
                    "message": "Account associated with this token does not exist",
                },
            )

        return user
    except InvalidTokenError as e:
        logger.error(e)
        raise HTTPException(detail={"message": "Invalid access token"}, status_code=400)
    except ExpiredSignatureError as e:
        logger.error(e)
        raise HTTPException(detail={"message": "Token has expired!"}, status_code=401)
