from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from motor.motor_asyncio import AsyncIOMotorClient
from ...utils import connect_to_database
from .model import User
from ...helpers import create_tokens
from .schema import LoginSchema
import bcrypt

auth = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@auth.post("/login")
async def login(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    validated_request: LoginSchema,
):
    user = await User.find_one(User.username == validated_request.username)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={"message": "Account does not exist"},
        )

    compare_password = bcrypt.checkpw(
        validated_request.password.encode("utf-8"),
        user.model_dump(mode="json").get("password").encode("utf-8"),
    )
    if not compare_password:
        raise HTTPException(status_code=401, detail={"message": "Invalid credentials"})

    access_token, refresh_token = create_tokens(user.model_dump(mode="json").get("id"))
    return JSONResponse(
        content={
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        },
        status_code=200,
    )
